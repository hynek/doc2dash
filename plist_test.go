// SPDX-License-Identifier: Apache-2.0

package doc2dash

import (
	"bytes"
	"strings"
	"testing"

	"howett.net/plist"

	"github.com/stretchr/testify/assert"
)

var goldenSimple = bytes.NewReader([]byte(`<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>attrs</string>
	<key>CFBundleName</key>
	<string>attrs</string>
	<key>DocSetPlatformFamily</key>
	<string>attrs</string>
	<key>isDashDocset</key>
	<true/>
	<key>DashDocSetFamily</key>
	<string>dashtoc</string>
</dict>
</plist>`))

func TestPlist(t *testing.T) {
	var goldenDsmd docSetMetaData
	decoder := plist.NewDecoder(goldenSimple)
	err := decoder.Decode(&goldenDsmd)

	assert.Nil(t, err)
	assert.True(t, goldenDsmd.IsDashDocset)

	t.Run("simple", func(t *testing.T) {
		t.Parallel()
		assert := assert.New(t)
		var buf strings.Builder

		err = writePlist(&buf, "attrs")
		assert.Nil(err)

		var dsmd docSetMetaData
		decoder := plist.NewDecoder(strings.NewReader(buf.String()))
		err := decoder.Decode(&dsmd)

		assert.Nil(err)
		assert.Equal(goldenDsmd, dsmd)
	})
}
