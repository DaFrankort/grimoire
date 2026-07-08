import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional

from python.spells.types import SpellComponent

SCRIPT_DIR = Path(__file__).parent.parent.parent
PATH_SRC = SCRIPT_DIR / "submodules" / "5e-src" / "data" / "spells"


@dataclass
class Spell:
    name: str
    source: str

    # Core metadata with simple defaults
    level: int = 0
    school: Optional[Literal["A", "C", "D", "E", "I", "N", "V", "T"]] = None
    page: Optional[int] = None

    # Booleans (Almost always omitted in raw JSON if False)
    basicRules: bool = False
    basicRules2024: bool = False
    hasFluff: bool = False
    hasFluffImages: bool = False
    srd: bool = False
    srd52: bool = False

    # Complex Structural Object Mappings
    components: dict[str, SpellComponent] = field(default_factory=dict)
    meta: dict[str, bool] = field(default_factory=dict)
    range: dict[str, Any] = field(default_factory=dict)  # Crucial: Dict, not List
    time: list[dict[str, Any]] = field(default_factory=list)
    duration: list[dict[str, Any]] = field(default_factory=list)
    scalingLevelDice: dict[str, Any] = field(default_factory=dict)

    # String arrays / Tags / Sub-lists
    abilityCheck: list[str] = field(default_factory=list)
    affectsCreatureType: list[str] = field(default_factory=list)
    alias: list[str] = field(default_factory=list)
    areaTags: list[Literal["MT", "ST"]] = field(default_factory=list)
    conditionImmune: list[str] = field(default_factory=list)
    conditionInflict: list[str] = field(default_factory=list)
    damageImmune: list[str] = field(default_factory=list)
    damageInflict: list[str] = field(default_factory=list)
    damageResist: list[str] = field(default_factory=list)
    damageVulnerable: list[str] = field(default_factory=list)
    miscTags: list[str] = field(default_factory=list)
    referenceSources: list[str] = field(default_factory=list)
    savingThrow: list[str] = field(default_factory=list)
    spellAttack: list[str] = field(default_factory=list)

    # Content/Text arrays (Often mixed types containing nested strings/objects)
    entries: list[Any] = field(default_factory=list)
    entriesHigherLevel: list[Any] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Spell":
        """Creates a Spell instance from a raw dictionary, filtering out extra keys."""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


class SpellList:
    entries: dict[str, dict[str, Spell]]
    sources: set[str]

    def __init__(self):
        self.entries = {}
        self.sources = set()
        self._load_entries()

    def _load_entries(self):
        src_index_path = PATH_SRC / "index.json"
        if not src_index_path.exists():
            logging.error(f"Index file not found at: {src_index_path.resolve()}")
            return

        logging.info(f"Loading spell-index {src_index_path}")
        with open(src_index_path, "r", encoding="utf-8") as index_file:
            index_data = json.load(index_file)

        paths: list[tuple[str, Path]] = []
        for source, filename in index_data.items():
            self.sources.add(source)
            paths.append((source, PATH_SRC / filename))

        for source, path in paths:
            if not path.exists():
                logging.warning(f"Spell file missing: {path.name}")
                continue

            logging.info(f"Loading spells - {path.name}")
            self.entries[source] = {}

            with open(path, "r", encoding="utf-8") as file:
                file_data = json.load(file)
                spells = file_data.get("spell", [])

                if len(spells) == 0:
                    logging.warning(f"Empty spell-list detected in {path}")

                for spell in spells:
                    name = spell.get("name")
                    logging.debug(f"- {name} {source}")
                    self.entries[source][name] = Spell.from_json(spell)

        logging.info(f"{len(self.entries)} Spells loaded.")

        output_path = Path(__file__).parent / "debug_parsed.json"
        with open(output_path, "w", encoding="utf-8") as out_file:
            # Dynamically convert the nested Spell objects into dictionaries
            serializable_entries = {
                source: {name: asdict(spell_obj) for name, spell_obj in spells_dict.items()}
                for source, spells_dict in self.entries.items()
            }

            json.dump(serializable_entries, out_file, indent=4, ensure_ascii=False)


def generate_spell_template():
    src_index_path = PATH_SRC / "index.json"
    if not src_index_path.exists():
        print(f"Error: Index file not found at {src_index_path}")
        return

    with open(src_index_path, "r", encoding="utf-8") as index_file:
        index_data = json.load(index_file)

    template_data: dict[str, Any] = {}
    EXCLUDED_KEYS = {"name", "source"}
    for _, filename in index_data.items():
        path = PATH_SRC / filename
        if not path.exists():
            continue

        with open(path, "r", encoding="utf-8") as file:
            try:
                file_data = json.load(file)
                spells = file_data.get("spell", [])

                for spell in spells:
                    for key, value in spell.items():
                        if key in EXCLUDED_KEYS or key in template_data:
                            continue
                        template_data[key] = value

            except json.JSONDecodeError:
                print(f"Skipping malformed JSON file: {path.name}")

    sorted_template = {k: template_data[k] for k in sorted(template_data.keys())}

    output_path = Path(__file__).parent / "spell_template.json"
    with open(output_path, "w", encoding="utf-8") as out_file:
        json.dump(sorted_template, out_file, indent=4, ensure_ascii=False)

    print(f"Successfully generated template with {len(sorted_template)} keys at: {output_path.resolve()}")


SPELLS = SpellList()
generate_spell_template()
