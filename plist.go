// SPDX-License-Identifier: Apache-2.0

package doc2dash

import (
	"fmt"
	"io"
	"os"
	"path/filepath"

	"howett.net/plist"
)

type docSetMetaData struct {
	IsDashDocset         bool `plist:"isDashDocset"`
	CFBundleIdentifier   string
	CFBundleName         string
	DocSetPlatformFamily string
	DashDocSetFamily     string
}

// WriteInfoPlistToDir writes an appropriate Info.plist to dir, based on
// the remaining arguments.
func WriteInfoPlistToDir(dir string, name string) error {
	path := filepath.Join(dir, "Info.plist")

	plistF, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("can't create plist file: %w", err)
	}
	defer plistF.Close()

	if err = writePlist(plistF, name); err != nil {
		return fmt.Errorf("can't write plist: %w", err)
	}

	return nil
}

// writePlist writes an appropriate plist to w, based on arguments.
func writePlist(w io.Writer, name string) error {
	encoder := plist.NewEncoder(w)

	return encoder.Encode(docSetMetaData{
		IsDashDocset:         true,
		CFBundleIdentifier:   name,
		CFBundleName:         name,
		DocSetPlatformFamily: name,
		DashDocSetFamily:     "dashtoc",
	})
}
