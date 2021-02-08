package parsers

import "errors"

// ErrNotMine means that the current parser cannot handle passed directory.
var ErrNotMine = errors.New("not my format")

// ErrInvalidFormat means that files exist, but we can't parse it.
var ErrInvalidFormat = errors.New("invalid format")
