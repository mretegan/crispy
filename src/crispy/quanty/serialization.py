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

    /                       datasets: format, format_version, crispy_version
    /<i>/                   one group per result; dataset type = calculation|external
      calculation:
        datasets: name, label, symbol, charge, symmetry, experiment, edge,
                  labelSuffix?, customLabel?, checkState, temperature,
                  magneticField, output?
        /Axes/              datasets: scale, normalization
          /XAxis/           datasets: shift, start, stop, npoints, gaussian,
                                      lorentzian, lorentzianPoints? (energy,
                                      FWHM) pairs
            /Photon/        datasets: k, e1, analyze (scattered photon only)
          /YAxis/           (two-dimensional experiments only)
        /Hamiltonian/       datasets: fk, gk, zeta, synchronizeParameters,
                                      numberOfStates, numberOfStatesAuto,
                                      numberOfConfigurations
          /Terms/<term>/    datasets: name, checkState
            /<hamiltonian>/
              /<parameter>/ datasets: name, value, scaleFactor
        /Spectra/
          toCalculate       dataset: selected spectrum names
          /Results/<j>/     datasets: type, name, suffix, label, lineStyle?,
                                      checkState, raw
      external:
        datasets: name, checkState, raw

The file stores every value as a dataset and has no attributes. Format version 1
stored most scalar values as attributes. :meth:`Serializer.read` reads both
layouts, so files of format version 1 continue to load.
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
FORMAT_VERSION = 2

STRING_DTYPE = h5py.string_dtype(encoding="utf-8")

_MISSING = object()


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
    def read(group, key, default=_MISSING):
        """Read the value of a dataset in the group.

        Format version 1 stored most scalar values as attributes. If the group
        has no dataset with the key, read the attribute with the key.

        Raises:
            KeyError: If the group has no dataset and no attribute with the key,
                and no default is given.
        """
        if key in group:
            return group[key][()]
        if key in group.attrs:
            return group.attrs[key]
        if default is _MISSING:
            raise KeyError(f"{group.name} has no value {key!r}.")
        return default

    @staticmethod
    def contains(group, key):
        """Return True if the group has a dataset or an attribute with the key."""
        return key in group or key in group.attrs

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
        group["shift"] = float(axis.shift.value)
        group["start"] = float(axis.start.value)
        group["stop"] = float(axis.stop.value)
        group["npoints"] = int(axis.npoints.value)
        group["gaussian"] = float(axis.gaussian.value)
        group["lorentzian"] = float(axis.lorentzian.value)
        group.create_dataset(
            "lorentzianPoints",
            data=np.asarray(axis.lorentzian.points.value, dtype=np.float64).reshape(
                -1, 2
            ),
        )

        photon = group.create_group("Photon")
        photon.create_dataset(
            "k", data=np.asarray(axis.photon.k.value, dtype=np.float64)
        )
        photon.create_dataset(
            "e1", data=np.asarray(axis.photon.e1.value, dtype=np.float64)
        )
        # Only the scattered photon resolves the outgoing polarization.
        if hasattr(axis.photon, "analyze"):
            photon["analyze"] = bool(axis.photon.analyze.value)

    def load(self, group, axis):
        axis.shift._value = float(self.read(group, "shift"))
        axis.start._value = float(self.read(group, "start"))
        axis.stop._value = float(self.read(group, "stop"))
        axis.npoints._value = int(self.read(group, "npoints"))
        axis.gaussian._value = float(self.read(group, "gaussian"))
        axis.lorentzian._value = float(self.read(group, "lorentzian"))
        # Files without the dataset use a constant Lorentzian broadening.
        if "lorentzianPoints" in group:
            axis.lorentzian.points._value = [
                (float(energy), float(fwhm))
                for energy, fwhm in group["lorentzianPoints"][()]
            ]

        photon = group["Photon"]
        axis.photon.k._value = np.asarray(photon["k"][()], dtype=np.float64)
        axis.photon.e1._value = np.asarray(photon["e1"][()], dtype=np.float64)
        if hasattr(axis.photon, "analyze") and self.contains(photon, "analyze"):
            axis.photon.analyze._value = bool(self.read(photon, "analyze"))
        axis.npoints._minimum = axis.npoints.minimum


class AxesSerializer(Serializer):
    """Serialize the axes container: scale, normalization, and the axes."""

    def __init__(self):
        self._axis = AxisSerializer()

    def save(self, group, axes):
        group["scale"] = float(axes.scale.value)
        group["normalization"] = str(axes.normalization.value)
        self._axis.save(group.create_group("XAxis"), axes.xaxis)
        if getattr(axes, "yaxis", None) is not None:
            self._axis.save(group.create_group("YAxis"), axes.yaxis)

    def load(self, group, axes):
        axes.scale._value = float(self.read(group, "scale"))
        axes.normalization._value = self.to_str(self.read(group, "normalization"))
        self._axis.load(group["XAxis"], axes.xaxis)
        if getattr(axes, "yaxis", None) is not None and "YAxis" in group:
            self._axis.load(group["YAxis"], axes.yaxis)


class HamiltonianSerializer(Serializer):
    """Serialize the Hamiltonian: scale factors, counts, and all terms."""

    def save(self, group, hamiltonian):
        group["fk"] = float(hamiltonian.fk.value)
        group["gk"] = float(hamiltonian.gk.value)
        group["zeta"] = float(hamiltonian.zeta.value)
        group["synchronizeParameters"] = bool(hamiltonian.synchronizeParameters.value)
        group["numberOfStates"] = int(hamiltonian.numberOfStates.value)
        group["numberOfStatesAuto"] = bool(hamiltonian.numberOfStates.auto.value)
        group["numberOfConfigurations"] = int(hamiltonian.numberOfConfigurations.value)

        terms = group.create_group("Terms")
        for term in hamiltonian.terms.children():
            termGroup = terms.create_group(self.escape(term.name))
            termGroup["name"] = term.name
            termGroup["checkState"] = int(term.checkState.value)
            # Each term groups its parameters under the initial, (intermediate,)
            # and final sub-Hamiltonians.
            for subHamiltonian in term.children():
                subGroup = termGroup.create_group(self.escape(subHamiltonian.name))
                # Each parameter is its own group, named after the parameter, so
                # the name is visible in the file layout rather than only as a
                # parallel attribute array.
                for parameter in subHamiltonian.children():
                    parameterGroup = subGroup.create_group(self.escape(parameter.name))
                    parameterGroup["name"] = parameter.name
                    parameterGroup.create_dataset(
                        "value", data=np.float64(parameter.value)
                    )
                    scaleFactor = parameter.scaleFactor
                    parameterGroup.create_dataset(
                        "scaleFactor",
                        data=np.float64(np.nan if scaleFactor is None else scaleFactor),
                    )

    def load(self, group, hamiltonian):
        hamiltonian.fk._value = float(self.read(group, "fk"))
        hamiltonian.gk._value = float(self.read(group, "gk"))
        hamiltonian.zeta._value = float(self.read(group, "zeta"))
        hamiltonian.synchronizeParameters._value = bool(
            self.read(group, "synchronizeParameters")
        )
        hamiltonian.numberOfStates._value = int(self.read(group, "numberOfStates"))
        hamiltonian.numberOfStates.auto._value = bool(
            self.read(group, "numberOfStatesAuto")
        )
        hamiltonian.numberOfConfigurations._value = int(
            self.read(group, "numberOfConfigurations")
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
            term._checkState = Qt.CheckState(int(self.read(termGroup, "checkState")))
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
            spectrumGroup["type"] = "2D" if isinstance(spectrum, Spectrum2D) else "1D"
            spectrumGroup["name"] = spectrum.name
            spectrumGroup["suffix"] = spectrum.suffix or ""
            spectrumGroup["label"] = spectrum.label or ""
            if spectrum.lineStyle is not None:
                spectrumGroup["lineStyle"] = spectrum.lineStyle
            spectrumGroup["checkState"] = int(spectrum.checkState.value)
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
            isTwoDimensional = self.to_str(self.read(spectrumGroup, "type")) == "2D"
            cls = Spectrum2D if isTwoDimensional else Spectrum1D
            spectrum = cls(
                parent=spectra.toPlot,
                name=self.to_str(self.read(spectrumGroup, "name")),
            )
            spectrum.suffix = self.to_str(self.read(spectrumGroup, "suffix")) or None
            spectrum.label = self.to_str(self.read(spectrumGroup, "label")) or None
            if self.contains(spectrumGroup, "lineStyle"):
                spectrum.lineStyle = self.to_str(self.read(spectrumGroup, "lineStyle"))
            if "raw" in spectrumGroup:
                spectrum.raw = np.asarray(spectrumGroup["raw"][()], dtype=np.float64)
                # Regenerate x/signal (and y) from the raw data and the axes.
                spectrum.process()
            spectrum._checkState = Qt.CheckState(
                int(self.read(spectrumGroup, "checkState"))
            )


class CalculationSerializer(Serializer):
    """Serialize a whole calculation by composing the component serializers."""

    def __init__(self):
        self._axes = AxesSerializer()
        self._hamiltonian = HamiltonianSerializer()
        self._spectra = SpectraSerializer()

    def save(self, group, calculation):
        group["type"] = "calculation"
        group["name"] = calculation.value
        group["label"] = calculation.label
        group["symbol"] = calculation.element.symbol
        group["charge"] = calculation.element.charge
        group["symmetry"] = calculation.symmetry.value
        group["experiment"] = calculation.experiment.value
        group["edge"] = calculation.edge.value
        if calculation.labelSuffix is not None:
            group["labelSuffix"] = calculation.labelSuffix
        if calculation.customLabel is not None:
            group["customLabel"] = calculation.customLabel
        group["checkState"] = int(calculation.checkState.value)
        group["temperature"] = int(calculation.temperature.value)
        group["magneticField"] = float(calculation.magneticField.value)
        # Keep the Quanty log so the details dialog can show it after a reload.
        if calculation.runner.output:
            group["output"] = calculation.runner.output

        self._axes.save(group.create_group("Axes"), calculation.axes)
        self._hamiltonian.save(
            group.create_group("Hamiltonian"), calculation.hamiltonian
        )
        self._spectra.save(group.create_group("Spectra"), calculation.spectra)

    def load(self, group, parent):
        calculation = Calculation(
            symbol=self.to_str(self.read(group, "symbol")),
            charge=self.to_str(self.read(group, "charge")),
            symmetry=self.to_str(self.read(group, "symmetry")),
            experiment=self.to_str(self.read(group, "experiment")),
            edge=self.to_str(self.read(group, "edge")),
            parent=parent,
        )

        name = self.to_str(self.read(group, "name"))
        if calculation.value != name:
            calculation._value = name
        if self.contains(group, "labelSuffix"):
            calculation.labelSuffix = self.to_str(self.read(group, "labelSuffix"))
        if self.contains(group, "customLabel"):
            calculation._customLabel = self.to_str(self.read(group, "customLabel"))
        calculation.temperature._value = int(self.read(group, "temperature"))
        calculation.magneticField._value = float(self.read(group, "magneticField"))
        if self.contains(group, "output"):
            calculation.runner.output = self.to_str(self.read(group, "output"))

        # The axes must be restored before the result spectra, which reprocess
        # their raw data using the axis ranges and broadenings.
        self._axes.load(group["Axes"], calculation.axes)
        self._hamiltonian.load(group["Hamiltonian"], calculation.hamiltonian)
        self._spectra.load(group["Spectra"], calculation.spectra)

        calculation._checkState = Qt.CheckState(int(self.read(group, "checkState")))
        return calculation


class ExternalDataSerializer(Serializer):
    """Serialize externally loaded data (a single curve)."""

    def save(self, group, external):
        group["type"] = "external"
        group["name"] = external.name
        group["checkState"] = int(external.checkState.value)
        if external.raw is not None:
            group.create_dataset("raw", data=np.asarray(external.raw, dtype=np.float64))

    def load(self, group, parent):
        raw = np.asarray(group["raw"][()], dtype=np.float64) if "raw" in group else None
        external = ExternalData(
            raw=raw, parent=parent, name=self.to_str(self.read(group, "name"))
        )
        external._checkState = Qt.CheckState(int(self.read(group, "checkState")))
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
        h5["format"] = FORMAT
        h5["format_version"] = FORMAT_VERSION
        h5["crispy_version"] = crispy_version
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
        if Serializer.to_str(Serializer.read(h5, "format", "")) != FORMAT:
            raise ValueError(f"{path} is not a Crispy results file.")
        fileVersion = int(Serializer.read(h5, "format_version", 0))
        if fileVersion > FORMAT_VERSION:
            raise ValueError(
                f"The file was written by a newer version of Crispy "
                f"(format version {fileVersion}); please update."
            )

        loaded = []
        # The root also holds the format datasets. Each result is a group.
        keys = [key for key, value in h5.items() if isinstance(value, h5py.Group)]
        for key in sorted(keys, key=int):
            group = h5[key]
            kind = Serializer.to_str(Serializer.read(group, "type", ""))
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
