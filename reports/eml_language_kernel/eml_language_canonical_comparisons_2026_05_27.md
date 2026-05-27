# EML-L2 Canonical Operator Tree Comparisons

Date: 2026-05-27

Status: `EML_CANONICAL_COMPARISONS_PASS`

| Pair | Equivalent | Left hash | Right hash |
|---|---:|---|---|
| eml primitive expansion | `True` | `sha256:870e00c09ae3236174b70fbb1dd0f27bef57c85481259c8180923991ad9e922c` | `sha256:870e00c09ae3236174b70fbb1dd0f27bef57c85481259c8180923991ad9e922c` |
| softplus expansion | `True` | `sha256:37a573a048a7e72ee7cce8ead6248c574e8164f218530b93cfaaea8bc6d725b7` | `sha256:37a573a048a7e72ee7cce8ead6248c574e8164f218530b93cfaaea8bc6d725b7` |
| guarded softplus EML expanded shape | `True` | `sha256:6a6fbd514b2283fdb15e2b1a58bf1a84ddbe379bf2b63c013f48860b636ca2f3` | `sha256:6a6fbd514b2283fdb15e2b1a58bf1a84ddbe379bf2b63c013f48860b636ca2f3` |
| commutative add canonicalization | `True` | `sha256:23d43f8e3d2d42a143388c180823be9d567fc81e16439b444acb142f3c6d7c3c` | `sha256:23d43f8e3d2d42a143388c180823be9d567fc81e16439b444acb142f3c6d7c3c` |
| commutative mul canonicalization | `True` | `sha256:c2aa9acb966e083d76ab86a4e081012517e80703c75728244beb658475204cbc` | `sha256:c2aa9acb966e083d76ab86a4e081012517e80703c75728244beb658475204cbc` |

## Boundary

- Structural canonicalization only.
- No semantic proof claim.
- No compiler rewrite claim.
- No public savings claim.
