# AlignmentDelta direction-source manifest specification

The source is the pinned `andyrdt/refusal_direction` repository at commit `9d852fae1a9121c78b29142de733cb1340770cc3` (Apache-2.0). The source files are referenced by blob ID rather than copied into this repository.

| Role | Source path | Blob ID | Record fields |
|---|---|---|---|
| harmful train | `dataset/splits/harmful_train.json` | `5ca6b46750e06bc401ebd93171a6b0dc0590cdd8` | source commit, blob, count 260, keys `instruction/category` |
| harmful validation | `dataset/splits/harmful_val.json` | `c3128d37e8b255e765f4f51f1a6715572595e3e7` | source commit, blob, count 39 |
| harmful test | `dataset/splits/harmful_test.json` | `2dc705dc1a50e7773efca46fedab71229169b3bb` | source commit, blob; count checked at data stage |
| harmless train | `dataset/splits/harmless_train.json` | `700a497bd1d20ab074fcc576e9bd79ac604543c5` | source commit, blob; count checked at data stage |
| harmless validation | `dataset/splits/harmless_val.json` | `6b9ee6e9c789799354b618a046758276da445bd8` | source commit, blob; count checked at data stage |
| harmless test | `dataset/splits/harmless_test.json` | `6033b711a3c0bf3d49fb88a4824fdac8be792f25` | source commit, blob; count checked at data stage |

AlignmentDelta uses only the train/validation roles for direction estimation and technical validation, with benchmark overlap checked by stable IDs before any primary run. Prompt text is not committed. The exact source split above is the original-paper reproduction choice; the AlignmentDelta role assignment and leakage audit are project choices.
