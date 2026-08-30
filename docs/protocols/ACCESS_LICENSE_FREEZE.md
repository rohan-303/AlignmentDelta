# Access and license freeze

| Asset | Source/revision | Evidence status | Terms/access finding | Final gate |
|---|---|---|---|---|
| Qwen2.5-3B-Instruct | HF, `aa8e72537993ba99e69dfaafa59ed015b17504d1` | API/config/tokenizer verified | Qwen Research License: non-commercial research/evaluation grant; attribution and notice requirements; no legal interpretation supplied | `cleared_with_restrictions` |
| Llama-3.2-3B-Instruct | HF, `0cb88a4f764b7a12671c53f0838cd831a0843b95` | API metadata verified; config/tokenizer blocked anonymously | manual gated; official license/use-policy files are listed but gated content was not independently inspected here | `blocked` |
| Gemma-2-2B-it | HF, `299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8` | API metadata verified; config/tokenizer blocked anonymously | manual gated; Google Gemma terms require direct review | `blocked` |
| Qwen2.5-1.5B-Instruct | HF, `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | API/config/tokenizer/meta architecture verified | Apache-2.0 file retrieved; attribution/license obligations apply | `cleared_with_restrictions` |
| Llama-3.2-1B-Instruct | HF, `9213176726f574b556790deb65791e0c5aa438b6` | API metadata verified; config/tokenizer blocked anonymously | manual gated; official license/use-policy files require direct review | `blocked` |
| SmolLM2-1.7B-Instruct | HF, `31b70e2e869a7173562077fd711b654946d38674` | API/config/tokenizer/meta architecture verified | API reports Apache-2.0; repository LICENSE path was not available at the checked URL, so terms must be re-recorded from the official card/repository before use | `cleared_with_restrictions` |
| Refusal-direction source | `andyrdt/refusal_direction`, `9d852fae1a9121c78b29142de733cb1340770cc3` | tree/source verified | Apache-2.0 repository; source data files are pinned by blob IDs and not redistributed here | `cleared_with_restrictions` |
| XSTest | `paul-rottger/xstest`, `d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d` | repo/file/blob metadata verified | CC-BY-4.0 repository metadata; local-use versus redistribution interpretation remains restricted | `cleared_with_restrictions` |
| HarmBench | `centerforaisafety/HarmBench`, `8e1604d1171fe8a48d8febecd22f600e462bdcdd` | repo/file/blob metadata verified | MIT repository metadata; evaluator/model terms are separate | `cleared_with_restrictions` |
| HarmBench classifier | `cais/HarmBench-Llama-2-13b-cls`, exact revision not yet accessible | official identity verified | 13B classifier; access, exact revision, and resource feasibility not cleared | `blocked` |
| MMLU | `hendrycks/test`, `4450500f923c49f1fb1dd3d99108a0bd9717b660` | repo metadata verified | MIT repository metadata; exact selected-file terms/hash must be attached before use | `cleared_with_restrictions` |
| Consistency pairs | future project manifest | not created | validation provenance and pair records required | `blocked` |

AlignmentDelta does not plan to redistribute third-party model weights. Derived scores may be publishable only after the applicable terms, access conditions, attribution, and institutional review are checked; this table is not legal advice.
