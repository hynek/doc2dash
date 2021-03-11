// SPDX-License-Identifier: Apache-2.0

package main

import (
	"context"
	"errors"
	"fmt"
	"image/png"
	"os"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/hynek/doc2dash"
	"github.com/hynek/doc2dash/parsers"
	"github.com/mitchellh/go-homedir"
	dirCopy "github.com/otiai10/copy"
	flag "github.com/spf13/pflag"
)

// checkIcon verifies that if an icon has been passed, it exists and is a PNG
// icon.
func checkIcon(p string) error {
	if p == "" {
		return nil
	}

	f, err := os.Open(p)
	if err != nil {
		return err
	}
	defer f.Close()

	_, err = png.Decode(f)
	if err != nil {
		return err
	}

	return nil
}

const plistTmpl = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>%s</string>
	<key>CFBundleName</key>
	<string>%s</string>
	<key>DocSetPlatformFamily</key>
	<string>%s</string>
	<key>isDashDocset</key>
	<true/>
	<key>DashDocSetFamily</key>
	<string>dashtoc</string>
</dict>
</plist>`

func run(
	src string,
	dest string,
	name string,
	force bool,
	icon string,
	indexPage string,
	addToDash bool,
	quiet bool,
	verbose bool,
	onlineRedirectURL string,
	enableJS bool,
) error {
	if quiet && verbose {
		return errors.New("can't be quiet and verbose at the same time")
	}

	// Check before we start doing expensive work.
	err := checkIcon(icon)
	if err != nil {
		return fmt.Errorf("couldn't open icon: %w", err)
	}

	fi, err := os.Stat(dest)
	if err != nil {
		return fmt.Errorf("can't access destination path: %w", err)
	}

	if !fi.IsDir() {
		return errors.New("destination is not a directory")
	}

	p, err := parsers.NewSphinxParser(src)
	if err != nil {
		if err == parsers.ErrNotMine {
			fmt.Println("No parser for passed directory.")
			return errors.New("unknown documentation format")
		}

		return fmt.Errorf("parsing failed: %w", err)
	}

	if name == "" {
		name = p.ProjectName + ".docset"
	}
	if strings.HasSuffix(strings.ToLower(name), ".docset") {
		name = name[:len(name)-7]
	}

	basePath, err := filepath.Abs(filepath.Join(dest, name+".docset"))
	if err != nil {
		return err
	}
	fmt.Println(basePath)

	if fi, err := os.Stat(basePath); fi != nil {
		if !force {
			return fmt.Errorf("destination path %s already exists", basePath)
		}

		fmt.Fprintf(os.Stderr, "Deleting existing %s...\n", basePath)
		err := os.RemoveAll(basePath)
		if err != nil {
			return fmt.Errorf("removing existing %s failed: %w", basePath, err)
		}
	} else if err != nil && !errors.Is(err, os.ErrNotExist) {
		return err
	}

	pContents := filepath.Join(basePath, "Contents")
	pResources := filepath.Join(pContents, "Resources")
	pDocuments := filepath.Join(pResources, "Documents")
	if err = os.MkdirAll(pDocuments, 0700); err != nil {
		return fmt.Errorf("can't create docset directory: %w", err)
	}

	err = os.WriteFile(
		filepath.Join(pContents, "Info.plist"),
		[]byte(fmt.Sprintf(plistTmpl, name, name, name)),
		0600,
	)
	if err != nil {
		return fmt.Errorf("can't create plist file: %w", err)
	}

	err = dirCopy.Copy(src, pDocuments)
	if err != nil {
		return fmt.Errorf("can't copy documentation tree into docset: %w", err)
	}

	db, err := doc2dash.InitIndexDB(filepath.Join(pResources, "docSet.dsidx"))
	if err != nil {
		return fmt.Errorf("can't create index file: %w", err)
	}
	defer db.Close()

	ctx, cancelFunc := context.WithCancel(context.Background())
	defer cancelFunc()

	ch, errc, err := p.StartParsing(ctx)
	if err != nil {
		return fmt.Errorf("parsing failed: %w", err)
	}
	numSym := 0

	for e := range ch {
		numSym++
		if verbose {
			fmt.Println(e)
		}

		err = db.AddDocEntry(e)
		if err != nil {
			cancelFunc()
			return fmt.Errorf("can't add doc entry to index: %w", err)
		}
	}

	if err = <-errc; err != nil {
		return fmt.Errorf("parsing failed: %w", err)
	}

	toPatch, err := db.IndexedFiles()
	if err != nil {
		return fmt.Errorf("reading indexed files failed: %w", err)
	}

	for _, file := range toPatch {
		lt, err := db.DocEntriesForFile(file)
		if err != nil {
			return fmt.Errorf("reading doc entries failed: %w", err)
		}

		err = doc2dash.PatchFile(filepath.Join(pDocuments, file), lt)
		if err != nil {
			return fmt.Errorf("could not patch file: %w", err)
		}
	}

	// fmt.Println(src, dest, force, icon, indexPage, addToDash, quiet, verbose)
	fmt.Println(numSym, name)

	return nil
}

func main() {
	dest := flag.StringP(
		"destination",
		"d",
		".",
		"Destination directory for docset.",
	)
	name := flag.StringP(
		"name",
		"n",
		"",
		"Name docset explicitly. Otherwise the name is guessed from the documentation.",
	)
	force := flag.BoolP(
		"force",
		"f",
		false,
		"Force overwriting if destination already exists.",
	)
	icon := flag.StringP(
		"icon",
		"i",
		"",
		"Add PNG icon to docset.",
	)
	indexPage := flag.StringP(
		"index-page",
		"I",
		"",
		"Set the file that is shown when the docset is clicked within Dash.app.",
	)
	quiet := flag.BoolP(
		"quiet",
		"q",
		false,
		"Limit output to errors and warnings.",
	)
	verbose := flag.BoolP(
		"verbose",
		"v",
		false,
		"Be verbose.",
	)
	onlineRedirectURL := flag.StringP(
		"online-redirect-url",
		"u",
		"",
		"The base URL of the online documentation.",
	)
	enableJS := flag.BoolP(
		"enable-js",
		"j",
		false,
		"Enable bundled and external Javascript.",
	)

	// The following options are only available on macOS.
	b := false
	addToGlobal := &b
	addToDash := &b
	var global *string
	if runtime.GOOS == "darwin" {
		addToDash = flag.BoolP(
			"add-to-dash",
			"a",
			false,
			"Automatically add resulting docset to Dash.app.",
		)

		docSetPath, err := homedir.Expand("~/Library/Application Support/doc2dash/DocSets")
		if err != nil {
			fmt.Fprintf(os.Stderr, "Could not resolve docset directory: %s\n", err)
			os.Exit(1)
		}

		addToGlobal = flag.BoolP(
			"add-to-global",
			"A",
			false,
			fmt.Sprintf(
				"Create docset in doc2dash's default global directory [%s] and add it to Dash.app.",
				docSetPath,
			),
		)

		global = &docSetPath
	}
	flag.Parse()

	if *addToGlobal {
		if *dest != "." {
			fmt.Fprintf(os.Stderr, "--destination and --add-to-global are mutually exclusive.\n")
			os.Exit(1)
		}

		dest = global
	}

	if err := run(
		flag.Arg(0),
		*dest,
		*name,
		*force,
		*icon,
		*indexPage,
		*addToDash,
		*quiet,
		*verbose,
		*onlineRedirectURL,
		*enableJS,
	); err != nil {
		fmt.Fprintf(os.Stderr, "doc2dash failed: %v\n", err)
		os.Exit(1)
	}
}
