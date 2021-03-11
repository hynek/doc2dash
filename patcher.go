// SPDX-License-Identifier: Apache-2.0

package doc2dash

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"

	"github.com/hynek/doc2dash/parsers"
	"golang.org/x/net/html"
)

// AnchorTmpl is a template string for Dash.app ToC anchors.
const AnchorTmpl = `<a name="//apple_ref/cpp/%s/%s" class="dashAnchor"></a>`

// PatchFile goes through in and whenever it encounters an item from docEntries,
// it adds a Dash.app anchor.
func PatchFile(
	path string,
	lt map[string]parsers.DocEntry,
) error {
	in, err := os.Open(path)
	if err != nil {
		return fmt.Errorf("could not read file for patching: %w", err)
	}
	defer in.Close()

	out, err := os.CreateTemp("", filepath.Base(path)+"_*")
	if err != nil {
		return fmt.Errorf("could not create temporary file for patching: %w", err)
	}
	defer os.Remove(out.Name())
	defer out.Close()

	// fmt.Println(out.Name())

	bOut := bufio.NewWriter(out)

	z := html.NewTokenizer(in)
	for {
		tt := z.Next()
		if tt == html.ErrorToken {
			// ...
			break
		}
		if tt == html.StartTagToken {
			t := z.Token()
			if t.Data == "a" {
				typ, name := needToPatch(t, lt)
				if typ != "" {
					// XXX: percent-escape!!!
					fmt.Fprintf(bOut, AnchorTmpl, typ, name)
				}
			}
		}

		_, err := bOut.WriteString(string(z.Raw()))
		if err != nil {
			return fmt.Errorf("could not write: %w", err)
		}
	}

	return os.Rename(out.Name(), path)
}

// XXX belongs to intersphinx
func needToPatch(
	t html.Token,
	lt map[string]parsers.DocEntry,
) (string, string) {
	var isHL bool
	var de parsers.DocEntry

	for _, ns := range t.Attr {
		if ns.Key == "class" {
			if ns.Val == "headerlink" {
				isHL = true
			}
		}
		if ns.Key == "href" {
			if d, ok := lt[ns.Val]; ok {
				de = d
			}
		}
	}

	if de != emptyDE && isHL {
		return string(de.Type), de.Name
	}

	return "", ""
}

var emptyDE = parsers.DocEntry{}
