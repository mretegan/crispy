"""Save and load Quanty calculations and external data to and from HDF5.

The format mirrors the way a calculation is normally created in the interface:
a fresh :class:`Calculation` is built from the five identity strings (symbol,
charge, symmetry, experiment, edge), which deterministically regenerates the
whole item tree, and the editable leaf values are then written on top, exactly
as :meth:`Calculation.copyFrom` does. Loading therefore reconstructs a fresh
calculation and restores the saved leaf values, the spectra selection, and the
computed result spectra.

Each model component has its own serializer (a :class:`Serializer` subclass)
that writes the component into an HDF5 group and restores it from one.
:class:`CalculationSerializer` composes the axes, Hamiltonian, and spectra
serializers; the module-level :func:`save_results` and :func:`load_results`
drive the whole file.

Layout of a file (track_order keeps the items in their original order)::

    /                       attrs: format, format_version, crispy_version
    /<i>/                   one group per result; attr type = calculation|external
      calculation:
        attrs: name, label, symbol, charge, symmetry, experiment, edge,
               labelSuffix?, customLabel?, checkState, temperature,
               magneticField, output?
        /Axes/              attrs: scale, normalization
          /XAxis/           attrs: shift, start, stop, npoints, gaussian, lorentzian
            /Photon/        datasets: k, e1; attr: analyze (scattered photon only)
          /YAxis/           (two-dimensional experiments only)
        /Hamiltonian/       attrs: fk, gk, zeta, synchronizeParameters,
                                   numberOfStates, numberOfStatesAuto,
                                   numberOfConfigurations
          /Terms/<term>/    attr: name, checkState
            /<hamiltonian>/
              /<parameter>/ datasets: value, scaleFactor; attr: name
        /Spectra/
          toCalculate       dataset: selected spectrum names
          /Results/<j>/     attrs: type, name, suffix, label, lineStyle?,
                                   checkState; dataset: raw
      external:
        attrs: name, checkState
        dataset: raw
"""

import logging

import h5py
import numpy as np
from silx.gui.qt import Qt

from crispy import version as crispy_version
from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation
from crispy.quanty.external import ExternalData
from crispy.quanty.spectra import Spectrum1D, Spectrum2D

logger = logging.getLogger(__name__)

# Preserve the order in which items are written so a reopened file shows the
# results in the same order, matching the convention used in generate.py.
h5py.get_config().track_order = True

FORMAT = "Crispy Results"
FORMAT_VERSION = 1

STRING_DTYPE = h5py.string_dtype(encoding="utf-8")


class Serializer:
    """Base class for the HDF5 serializers of the result-tree components.

    A serializer writes one model component into an HDF5 group with save() and
    restores it from one with load(). The static helpers handle the low-level
    string and name conversions shared by all serializers.
    """

    @staticmethod
    def to_str(value):
        """Decode an HDF5 scalar string (bytes or str) to a Python str."""
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    @staticmethod
    def to_str_list(value):
        """Decode an HDF5 string array (attribute or dataset) to a list of str."""
        values = np.atleast_1d(np.asarray(value, dtype=object))
        return [Serializer.to_str(v) for v in values]

    @staticmethod
    def escape(name):
        """Make an item name safe to use as an HDF5 group name.

        HDF5 treats "/" as a path separator, so it cannot appear in a name. None
        of the names stored as group names currently contain it, but the escape
        keeps the format robust if that ever changes.
        """
        return name.replace("/", "∕")  # noqa: RUF001  (U+2215 division slash)


class AxisSerializer(Serializer):
    """Serialize a single axis: its ranges, broadenings, and photon vectors."""

    def save(self, group, axis):
        group.attrs["shift"] = float(axis.shift.value)
        group.attrs["start"] = float(axis.start.value)
        group.attrs["stop"] = float(axis.stop.value)
        group.attrs["npoints"] = int(axis.npoints.value)
        group.attrs["gaussian"] = float(axis.gaussian.value)
        group.attrs["lorentzian"] = float(axis.lorentzian.value)

        photon = group.create_group("Photon")
        photon.create_dataset(
            "k", data=np.asarray(axis.photon.k.value, dtype=np.float64)
        )
        photon.create_dataset(
            "e1", data=np.asarray(axis.photon.e1.value, dtype=np.float64)
        )
        # Only the scattered photon resolves the outgoing polarization.
        if hasattr(axis.photon, "analyze"):
            photon.attrs["analyze"] = bool(axis.photon.analyze.value)

    def load(self, group, axis):
        axis.shift._value = float(group.attrs["shift"])
        axis.start._value = float(group.attrs["start"])
        axis.stop._value = float(group.attrs["stop"])
        axis.npoints._value = int(group.attrs["npoints"])
        axis.gaussian._value = float(group.attrs["gaussian"])
        axis.lorentzian._value = float(group.attrs["lorentzian"])

        photon = group["Photon"]
        axis.photon.k._value = np.asarray(photon["k"][()], dtype=np.float64)
        axis.photon.e1._value = np.asarray(photon["e1"][()], dtype=np.float64)
        if hasattr(axis.photon, "analyze") and "analyze" in photon.attrs:
            axis.photon.analyze._value = bool(photon.attrs["analyze"])


class AxesSerializer(Serializer):
    """Serialize the axes container: scale, normalization, and the axes."""

    def __init__(self):
        self._axis = AxisSerializer()

    def save(self, group, axes):
        group.attrs["scale"] = float(axes.scale.value)
        group.attrs["normalization"] = str(axes.normalization.value)
        self._axis.save(group.create_group("XAxis"), axes.xaxis)
        if getattr(axes, "yaxis", None) is not None:
            self._axis.save(group.create_group("YAxis"), axes.yaxis)

    def load(self, group, axes):
        axes.scale._value = float(group.attrs["scale"])
        axes.normalization._value = self.to_str(group.attrs["normalization"])
        self._axis.load(group["XAxis"], axes.xaxis)
        if getattr(axes, "yaxis", None) is not None and "YAxis" in group:
            self._axis.load(group["YAxis"], axes.yaxis)


class HamiltonianSerializer(Serializer):
    """Serialize the Hamiltonian: scale factors, counts, and all terms."""

    def save(self, group, hamiltonian):
        group.attrs["fk"] = float(hamiltonian.fk.value)
        group.attrs["gk"] = float(hamiltonian.gk.value)
        group.attrs["zeta"] = float(hamiltonian.zeta.value)
        group.attrs["synchronizeParameters"] = bool(
            hamiltonian.synchronizeParameters.value
        )
        group.attrs["numberOfStates"] = int(hamiltonian.numberOfStates.value)
        group.attrs["numberOfStatesAuto"] = bool(hamiltonian.numberOfStates.auto.value)
        group.attrs["numberOfConfigurations"] = int(
            hamiltonian.numberOfConfigurations.value
        )

        terms = group.create_group("Terms")
        for term in hamiltonian.terms.children():
            termGroup = terms.create_group(self.escape(term.name))
            termGroup.attrs["name"] = term.name
            termGroup.attrs["checkState"] = int(term.checkState.value)
            # Each term groups its parameters under the initial, (intermediate,)
            # and final sub-Hamiltonians.
            for subHamiltonian in term.children():
                subGroup = termGroup.create_group(self.escape(subHamiltonian.name))
                # Each parameter is its own group, named after the parameter, so
                # the name is visible in the file layout rather than only as a
                # parallel attribute array.
                for parameter in subHamiltonian.children():
                    parameterGroup = subGroup.create_group(self.escape(parameter.name))
                    parameterGroup.attrs["name"] = parameter.name
                    parameterGroup.create_dataset(
                        "value", data=np.float64(parameter.value)
                    )
                    scaleFactor = parameter.scaleFactor
                    parameterGroup.create_dataset(
                        "scaleFactor",
                        data=np.float64(np.nan if scaleFactor is None else scaleFactor),
                    )

    def load(self, group, hamiltonian):
        hamiltonian.fk._value = float(group.attrs["fk"])
        hamiltonian.gk._value = float(group.attrs["gk"])
        hamiltonian.zeta._value = float(group.attrs["zeta"])
        hamiltonian.synchronizeParameters._value = bool(
            group.attrs["synchronizeParameters"]
        )
        hamiltonian.numberOfStates._value = int(group.attrs["numberOfStates"])
        hamiltonian.numberOfStates.auto._value = bool(group.attrs["numberOfStatesAuto"])
        hamiltonian.numberOfConfigurations._value = int(
            group.attrs["numberOfConfigurations"]
        )

        terms = group["Terms"]
        for term in hamiltonian.terms.children():
            key = self.escape(term.name)
            if key not in terms:
                logger.warning(
                    "Term %r is missing in the file; using defaults.", term.name
                )
                continue
            termGroup = terms[key]
            term._checkState = Qt.CheckState(int(termGroup.attrs["checkState"]))
            for subHamiltonian in term.children():
                subKey = self.escape(subHamiltonian.name)
                if subKey not in termGroup:
                    continue
                subGroup = termGroup[subKey]
                # Match by group name so a reordered or extended parameter set
                # loads; missing parameters keep their defaults.
                for parameter in subHamiltonian.children():
                    parameterKey = self.escape(parameter.name)
                    if parameterKey not in subGroup:
                        continue
                    parameterGroup = subGroup[parameterKey]
                    parameter._value = float(parameterGroup["value"][()])
                    scaleFactor = parameterGroup["scaleFactor"][()]
                    parameter._scaleFactor = (
                        None if np.isnan(scaleFactor) else float(scaleFactor)
                    )


class SpectraSerializer(Serializer):
    """Serialize the spectra: the to-calculate selection and the results."""

    def save(self, group, spectra):
        selected = list(spectra.toCalculate.selected)
        group.create_dataset(
            "toCalculate", data=np.asarray(selected, dtype=STRING_DTYPE)
        )

        results = group.create_group("Results")
        for index, spectrum in enumerate(spectra.toPlot.children()):
            spectrumGroup = results.create_group(str(index))
            spectrumGroup.attrs["type"] = (
                "2D" if isinstance(spectrum, Spectrum2D) else "1D"
            )
            spectrumGroup.attrs["name"] = spectrum.name
            spectrumGroup.attrs["suffix"] = spectrum.suffix or ""
            spectrumGroup.attrs["label"] = spectrum.label or ""
            if spectrum.lineStyle is not None:
                spectrumGroup.attrs["lineStyle"] = spectrum.lineStyle
            spectrumGroup.attrs["checkState"] = int(spectrum.checkState.value)
            if spectrum.raw is not None:
                spectrumGroup.create_dataset(
                    "raw", data=np.asarray(spectrum.raw, dtype=np.float64)
                )

    def load(self, group, spectra):
        if "toCalculate" in group:
            names = self.to_str_list(group["toCalculate"][()])
            spectra.toCalculate.selected = set(names)

        results = group.get("Results")
        if results is None:
            return
        for key in sorted(results, key=int):
            spectrumGroup = results[key]
            isTwoDimensional = self.to_str(spectrumGroup.attrs["type"]) == "2D"
            cls = Spectrum2D if isTwoDimensional else Spectrum1D
            spectrum = cls(
                parent=spectra.toPlot, name=self.to_str(spectrumGroup.attrs["name"])
            )
            spectrum.suffix = self.to_str(spectrumGroup.attrs["suffix"]) or None
            spectrum.label = self.to_str(spectrumGroup.attrs["label"]) or None
            if "lineStyle" in spectrumGroup.attrs:
                spectrum.lineStyle = self.to_str(spectrumGroup.attrs["lineStyle"])
            if "raw" in spectrumGroup:
                spectrum.raw = np.asarray(spectrumGroup["raw"][()], dtype=np.float64)
                # Regenerate x/signal (and y) from the raw data and the axes.
                spectrum.process()
            spectrum._checkState = Qt.CheckState(int(spectrumGroup.attrs["checkState"]))


class CalculationSerializer(Serializer):
    """Serialize a whole calculation by composing the component serializers."""

    def __init__(self):
        self._axes = AxesSerializer()
        self._hamiltonian = HamiltonianSerializer()
        self._spectra = SpectraSerializer()

    def save(self, group, calculation):
        group.attrs["type"] = "calculation"
        group.attrs["name"] = calculation.value
        group.attrs["label"] = calculation.label
        group.attrs["symbol"] = calculation.element.symbol
        group.attrs["charge"] = calculation.element.charge
        group.attrs["symmetry"] = calculation.symmetry.value
        group.attrs["experiment"] = calculation.experiment.value
        group.attrs["edge"] = calculation.edge.value
        if calculation.labelSuffix is not None:
            group.attrs["labelSuffix"] = calculation.labelSuffix
        if calculation.customLabel is not None:
            group.attrs["customLabel"] = calculation.customLabel
        group.attrs["checkState"] = int(calculation.checkState.value)
        group.attrs["temperature"] = int(calculation.temperature.value)
        group.attrs["magneticField"] = float(calculation.magneticField.value)
        # Keep the Quanty log so the details dialog can show it after a reload.
        if calculation.runner.output:
            group.attrs["output"] = calculation.runner.output

        self._axes.save(group.create_group("Axes"), calculation.axes)
        self._hamiltonian.save(
            group.create_group("Hamiltonian"), calculation.hamiltonian
        )
        self._spectra.save(group.create_group("Spectra"), calculation.spectra)

    def load(self, group, parent):
        calculation = Calculation(
            symbol=self.to_str(group.attrs["symbol"]),
            charge=self.to_str(group.attrs["charge"]),
            symmetry=self.to_str(group.attrs["symmetry"]),
            experiment=self.to_str(group.attrs["experiment"]),
            edge=self.to_str(group.attrs["edge"]),
            parent=parent,
        )

        name = self.to_str(group.attrs["name"])
        if calculation.value != name:
            calculation._value = name
        if "labelSuffix" in group.attrs:
            calculation.labelSuffix = self.to_str(group.attrs["labelSuffix"])
        if "customLabel" in group.attrs:
            calculation._customLabel = self.to_str(group.attrs["customLabel"])
        calculation.temperature._value = int(group.attrs["temperature"])
        calculation.magneticField._value = float(group.attrs["magneticField"])
        if "output" in group.attrs:
            calculation.runner.output = self.to_str(group.attrs["output"])

        # The axes must be restored before the result spectra, which reprocess
        # their raw data using the axis ranges and broadenings.
        self._axes.load(group["Axes"], calculation.axes)
        self._hamiltonian.load(group["Hamiltonian"], calculation.hamiltonian)
        self._spectra.load(group["Spectra"], calculation.spectra)

        calculation._checkState = Qt.CheckState(int(group.attrs["checkState"]))
        return calculation


class ExternalDataSerializer(Serializer):
    """Serialize externally loaded data (a single curve)."""

    def save(self, group, external):
        group.attrs["type"] = "external"
        group.attrs["name"] = external.name
        group.attrs["checkState"] = int(external.checkState.value)
        if external.raw is not None:
            group.create_dataset("raw", data=np.asarray(external.raw, dtype=np.float64))

    def load(self, group, parent):
        raw = np.asarray(group["raw"][()], dtype=np.float64) if "raw" in group else None
        external = ExternalData(
            raw=raw, parent=parent, name=self.to_str(group.attrs["name"])
        )
        external._checkState = Qt.CheckState(int(group.attrs["checkState"]))
        return external


def save_results(items, path):
    """Save calculations and external data to an HDF5 file.

    Args:
        items: Iterable of Calculation and ExternalData objects. Items of any
            other type are ignored.
        path: Destination file path.
    """
    items = [item for item in items if isinstance(item, (Calculation, ExternalData))]
    calculationSerializer = CalculationSerializer()
    externalSerializer = ExternalDataSerializer()

    with h5py.File(path, "w") as h5:
        h5.attrs["format"] = FORMAT
        h5.attrs["format_version"] = FORMAT_VERSION
        h5.attrs["crispy_version"] = crispy_version
        for index, item in enumerate(items):
            group = h5.create_group(str(index))
            if isinstance(item, Calculation):
                calculationSerializer.save(group, item)
            else:
                externalSerializer.save(group, item)


def load_results(path, parent):
    """Load calculations and external data from an HDF5 file.

    The loaded items are attached to ``parent`` (the root item of the results
    model), so they appear in the results view.

    Each item is first built in a private staging model and only re-parented to
    ``parent`` once it is fully restored. Attaching a half-built calculation to
    the results model would emit the change signals it connects to (e.g. the
    plot refresh) before the calculation is usable; this mirrors how the rest of
    the application builds a calculation elsewhere and moves it into the results
    model only when it is complete.

    Args:
        path: Source file path.
        parent: Root item the loaded items are attached to.

    Returns:
        The list of loaded Calculation and ExternalData objects.

    Raises:
        ValueError: If the file is not a Crispy results file or its version is
            newer than this version of Crispy understands.
    """
    staging = TreeModel()
    stagingRoot = staging.rootItem()
    calculationSerializer = CalculationSerializer()
    externalSerializer = ExternalDataSerializer()

    with h5py.File(path, "r") as h5:
        if Serializer.to_str(h5.attrs.get("format", "")) != FORMAT:
            raise ValueError(f"{path} is not a Crispy results file.")
        fileVersion = int(h5.attrs.get("format_version", 0))
        if fileVersion > FORMAT_VERSION:
            raise ValueError(
                f"The file was written by a newer version of Crispy "
                f"(format version {fileVersion}); please update."
            )

        loaded = []
        for key in sorted(h5, key=int):
            group = h5[key]
            kind = Serializer.to_str(group.attrs.get("type", ""))
            try:
                if kind == "calculation":
                    loaded.append(calculationSerializer.load(group, stagingRoot))
                elif kind == "external":
                    loaded.append(externalSerializer.load(group, stagingRoot))
                else:
                    logger.warning("Skipping item %s of unknown type %r.", key, kind)
            except (KeyError, ValueError) as e:
                logger.error("Failed to load item %s: %s", key, e)

    # Move the completed items from the staging model into the results model.
    for item in loaded:
        item.setParent(parent)
    return loaded
