package parsers

import (
	"errors"
)

// ErrNotMine means that the current parser cannot handle passed directory.
var ErrNotMine = errors.New("not my format")

// InvalidFormatError means that files exist, but we can't parse them.
type InvalidFormatError struct {
	Err error
}

func (ife *InvalidFormatError) Error() string {
	return "invalid format: " + ife.Err.Error()
}
