# Timeless Matrix

A NumPy-based **two-dimensional matrix** supporting row/column insertion and deletion plus **selective cell-level rewind**. Restore particular coordinates from an earlier matrix version while leaving the other current cells untouched.

> The source filename and class name intentionally use the spelling `timless_matrix`.

## Features

- Uses `numpy.float32` for matrix storage.
- Inserts or removes entire rows (`axis=0`) and columns (`axis=1`).
- Restores one or many `(row, column)` coordinates from a previous version.
- Saves full independent matrix snapshots after supported modifications.
- Uses preallocated NumPy arrays and slice assignments rather than `np.insert` or `np.delete`.

## Requirements

- Python 3
- NumPy

```bash
pip install numpy
```

## Quick start

Place `timless_matrix.py` in your project directory:

```python
from timless_matrix import timless_matrix

matrix = timless_matrix([
    [1, 2],
    [3, 4]
])

matrix.add_to_array([5, 6], to_end=True, axis=0)
# [[1., 2.],
#  [3., 4.],
#  [5., 6.]]

matrix.add_to_array([7, 8, 9], to_end=True, axis=1)
# [[1., 2., 7.],
#  [3., 4., 8.],
#  [5., 6., 9.]]

matrix.rewind([(0, 0), (1, 1)], how_far_back=2)
# Restores those cells from the original 2x2 version.

print(matrix.array)
```

## API

| Method | Description |
| --- | --- |
| `timless_matrix(array)` | Initialize from a 2D array-like input, converted to `float32`. |
| `add_to_array(value, index=None, to_end=False, axis=0)` | Insert a full row (`axis=0`) or column (`axis=1`). |
| `remove_from_array(index, axis=0)` | Delete a row or column at `index`. |
| `rewind(index, how_far_back)` | Restore one `(row, column)` pair or multiple coordinate pairs from a past snapshot. |
| `update_history(new_array)` | Append a matrix reference to history; intended for internal use. |

### Insert and remove

```python
matrix = timless_matrix([[1, 2], [3, 4]])

matrix.add_to_array([5, 6], index=1, axis=0)  # Insert row
matrix.add_to_array([7, 8, 9], to_end=True, axis=1)  # Append column
matrix.remove_from_array(0, axis=1)  # Remove first column
```

The inserted row or column must be a **1D sequence whose length matches the other matrix dimension**. `axis` must be `0` or `1`.

### Selective rewind

```python
matrix = timless_matrix([[10, 20], [30, 40]])
matrix.add_to_array([50, 60], to_end=True, axis=0)

matrix.rewind([(0, 1), (1, 0)], how_far_back=1)
print(matrix.array)
# [[10. 20.]
#  [30. 40.]
#  [50. 60.]]
```

- `how_far_back=1` selects the immediately previous version; higher values reach further back.
- Pass `[(row, col), ...]` or a single `(row, col)` pair.
- If any coordinate is missing from the selected historical matrix, the method returns `"Index does not exist in this past instance!"` without changing the current matrix.
- Coordinates outside the current matrix raise `IndexError`.
- A successful nonempty rewind creates a new full snapshot.
- Coordinates are **positional**, not persistent row/column identities. Structural changes can make the same coordinates refer to different logical cells in different versions.

## Performance and memory

This implementation prioritizes simple NumPy operations and exact `float32` historical values over storage efficiency. Each operation that changes the matrix allocates a new full matrix; rewinding even one cell also copies the current matrix.

For a **5,000 × 5,000 `float32` matrix**, each full snapshot occupies approximately **95.37 MiB**. Eight equally sized snapshots would occupy approximately **763 MiB**, excluding overhead. Adding/removing rows or columns changes the size of individual snapshots.

## Design considerations

- **Exact history:** Stored snapshots preserve historical `float32` values.
- **Memory cost:** Snapshot storage grows roughly with the sum of all historical matrix sizes.
- **Position-based history:** Inserted/deleted rows and columns can shift coordinate meanings.
- **Mutation safety:** Avoid editing `matrix.array` or `matrix.array_history` in place; doing so can bypass or corrupt version tracking.
- **Scope:** This is a numerical matrix utility, not a layer-aware image editor or a compressed-history engine.

## License

No license is included by default. Add a `LICENSE` file before distributing under specific reuse terms.
