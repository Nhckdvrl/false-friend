"""New English/German lexical cases and English polysemy; exploratory, authored locally."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

# Sentences are newly authored, not dictionary examples. German senses were checked
# against the linked dictionary; local readings, not exhaustive disjoint sense sets.
FALSE_FRIENDS = [
    ("gift", ["a poisonous substance", "an item given to someone as a present"],
     "Sie untersuchte [das Gift].", "Sie untersuchte [die giftige Substanz].",
     "She wrapped [the gift].", "She wrapped [the present].",
     "https://dictionary.cambridge.org/us/dictionary/english-german/poison"),
    ("rat", ["advice about what to do", "a rodent animal"],
     "Sie dachte über [seinen Rat] nach.", "Sie dachte über [seinen Ratschlag] nach.",
     "She saw [a rat] near the wall.", "She saw [a rodent] near the wall.",
     "https://www.duden.de/rechtschreibung/Rat"),
    ("chef", ["the person in charge of a workplace", "a professional cook"],
     "Er sprach mit [seinem Chef].", "Er sprach mit [seinem Vorgesetzten].",
     "She spoke to [the chef].", "She spoke to [the professional cook].",
     "https://www.duden.de/rechtschreibung/Chef"),
    ("rock", ["a skirt worn as clothing", "a piece of stone"],
     "Sie kaufte [einen Rock].", "Sie kaufte [ein unten offenes Kleidungsstück, das von der Taille herabhängt].",
     "He picked up [a rock] from the ground.", "He picked up [a stone] from the ground.",
     "https://www.duden.de/rechtschreibung/Rock_Kleidungsstueck"),
    ("hut", ["a hat worn on the head", "a small simple building used as a shelter"],
     "Sie setzte [den Hut] auf.", "Sie setzte [die Kopfbedeckung] auf.",
     "They slept in [the hut].", "They slept in [the small shelter].",
     "https://www.duden.de/rechtschreibung/Hut_Kopfbedeckung"),
    ("mist", ["animal manure used as fertilizer", "tiny water droplets suspended in the air"],
     "Der Bauer verteilte [den Mist] auf dem Feld.", "Der Bauer verteilte [den tierischen Dung] auf dem Feld.",
     "She saw [the mist] above the lake.", "She saw [the thin fog] above the lake.",
     "https://www.duden.de/rechtschreibung/Mist_Dreck"),
    ("boot", ["a small vessel that travels on water", "a shoe covering the foot and ankle"],
     "Er reparierte [das Boot].", "Er reparierte [das kleine Wasserfahrzeug].",
     "She laced up [the boot].", "She laced up [the ankle-covering shoe].",
     "https://www.duden.de/rechtschreibung/Boot_Wasserfahrzeug"),
    ("angel", ["a rod with a line and hook used for catching fish", "a supernatural heavenly being"],
     "Sie nahm [die Angel] zum Fischen mit.", "Sie nahm [die Fischerrute] zum Fischen mit.",
     "In the story, [an angel] descended from heaven.", "In the story, [a heavenly being] descended from heaven.",
     "https://www.duden.de/rechtschreibung/Angel"),
]

POLYSEMY = [
    ("bank", ["an institution that holds money", "the ground along a river"],
     "She deposited her wages at [the bank].", "She deposited her wages at [the financial institution].",
     "The fisherman sat on [the bank] beside the river.", "The fisherman sat on [the riverside ground] beside the river."),
    ("bat", ["a flying mammal", "a club used to hit a ball in a sport"],
     "At dusk, [the bat] flew out of the cave.", "At dusk, [the flying mammal] flew out of the cave.",
     "The player swung [the bat] at the ball.", "The player swung [the hitting club] at the ball."),
    ("crane", ["a long-legged bird", "a machine for lifting heavy loads"],
     "[The crane] spread its wings in the marsh.", "[The long-legged bird] spread its wings in the marsh.",
     "[The crane] lifted a steel beam at the construction site.", "[The lifting machine] lifted a steel beam at the construction site."),
    ("seal", ["a marine mammal", "a wax mark that closes a document"],
     "[The seal] swam toward the fish.", "[The marine mammal] swam toward the fish.",
     "She broke [the seal] of wax on the letter.", "She broke [the closing mark] of wax on the letter."),
    ("spring", ["the season after winter", "a coiled elastic mechanical component"],
     "The flowers returned in [the spring].", "The flowers returned in [the season after winter].",
     "The mechanic compressed [the spring] inside the lock.", "The mechanic compressed [the elastic coil] inside the lock."),
    ("mouse", ["a small rodent animal", "a hand-held computer pointing device"],
     "[The mouse] nibbled the cheese.", "[The small rodent] nibbled the cheese.",
     "She connected [the mouse] to the laptop's USB port.", "She connected [the pointing device] to the laptop's USB port."),
    ("bark", ["the outer covering of a tree trunk", "a short loud sound made by a dog"],
     "The insect hid under [the bark] of the tree.", "The insect hid under [the outer protective layer] of the tree.",
     "She heard [the bark] of a dog.", "She heard [the short loud sound] of a dog."),
    ("pitcher", ["a container for pouring drinks", "a baseball player who throws the ball to the batter"],
     "She poured water from [the pitcher].", "She poured water from [the pouring jug].",
     "[The pitcher] threw the ball toward the batter.", "[The baseball thrower] threw the ball toward the batter."),
]


def build():
    rows = []
    for group, source in [("cross_language", FALSE_FRIENDS), ("within_english", POLYSEMY)]:
        for number, spec in enumerate(source):
            word, meanings, first, first_para, second, second_para, *sources = spec
            order = [number % 2, 1 - number % 2]
            definitions = [meanings[j] for j in order]
            family = f"{group}:{word}"
            for sense, (original, paraphrase) in enumerate([(first, first_para), (second, second_para)]):
                assert len(re.findall(r"\[[^\]]+\]", original)) == 1
                assert re.sub(r"\[[^\]]+\]", "SLOT", original) == re.sub(r"\[[^\]]+\]", "SLOT", paraphrase)
                rows.append({"schema_version": "output-language-cycle-v1", "item_id": f"{family}:{sense}",
                             "lexeme_family_id": family, "lexeme": word, "group": group,
                             "source_language": "de" if group == "cross_language" and sense == 0 else "en",
                             "sense_index": order.index(sense), "definitions": definitions,
                             "contexts": {"original": original, "paraphrase": paraphrase,
                                          "masked": re.sub(r"\[[^\]]+\]", "[expression removed]", original)},
                             "lexical_reference_urls": sources,
                             "review": {"type": "single_research_agent_not_human", "status": "reviewed_before_model_outputs",
                                        "scope": "Local literal sense, grammar, one replaced phrase; paraphrases are more explicit, not length-matched.",
                                        "limits": "Concepts may overlap as real-world properties; task asks conveyed meaning. No whole-word exclusivity claim; control groups not psycholinguistically matched."},
                             "provenance": {"sentences": "newly authored in this workbench", "selection": "exploratory after cycle1; no outputs on these authored items examined", "heldout": False}})
    assert len(rows) == 32
    return rows


if __name__ == "__main__":
    destination = ROOT / "experiments/stimuli/output_language_cycle_v1.jsonl"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in build()))
    print(destination, hashlib.sha256(destination.read_bytes()).hexdigest())
