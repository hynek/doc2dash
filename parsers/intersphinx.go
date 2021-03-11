package parsers

import (
	"bufio"
	"compress/zlib"
	"context"
	"errors"
	"fmt"
	"io"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/ryboe/q"
)

// IntersphinxParser parses Sphinx-style objects.inv-indexed documentation.
type IntersphinxParser struct {
	DirName     string
	ProjectName string
	Version     string
	objInv      io.ReadCloser
}

// NewSphinxParser creates a new Sphinx parser for dirName of dirName
// is in Sphinx format.
func NewSphinxParser(dirName string) (*IntersphinxParser, error) {
	ours, err := isMine(dirName)
	if err != nil {
		return nil, err
	}
	if !ours {
		return nil, ErrNotMine
	}

	f, err := os.Open(filepath.Join(dirName, "objects.inv"))
	if err != nil {
		return nil, err
	}

	r := bufio.NewReader(f)

	pn, ver, err := parseHeader(r)
	if err != nil {
		return nil, fmt.Errorf(
			"%w: can't parse header: %w",
			ErrInvalidFormat,
			err,
		)
	}

	zr, err := zlib.NewReader(r)
	if err != nil {
		return nil, err
	}

	return &IntersphinxParser{
		dirName,
		pn,
		ver,
		zr,
	}, nil
}

// StartParsing starts a go routine that send DocEntrys and signals errors.
func (sp *IntersphinxParser) StartParsing(ctx context.Context) (<-chan *DocEntry, <-chan error, error) {
	ch := make(chan *DocEntry)
	errc := make(chan error, 1)

	s := bufio.NewScanner(sp.objInv)

	go func() {
		defer close(ch)
		defer close(errc)
		defer sp.objInv.Close()

		for s.Scan() {
			select {
			case ch <- makeEntry(s.Text()):
			case <-ctx.Done():
				return
			}
		}

		if err := s.Err(); err != nil {
			errc <- fmt.Errorf("parsing failed: %w", err)
		}
	}()

	return ch, errc, nil
}

// Close closes the underlying file.
func (sp *IntersphinxParser) Close() {
	sp.objInv.Close()
}

var roleToType = map[string]DocEntryType{
	"attribute":    EntryAttribute,
	"class":        EntryClass,
	"classmethod":  EntryMethod,
	"constant":     EntryConstant,
	"data":         EntryValue,
	"envvar":       EntryEnvironment,
	"exception":    EntryException,
	"function":     EntryFunction,
	"interface":    EntryInterface,
	"label":        EntrySection,
	"macro":        EntryMacro,
	"member":       EntryAttribute,
	"method":       EntryMethod,
	"module":       EntryModule,
	"opcode":       EntryOperator,
	"option":       EntryOption,
	"staticmethod": EntryMethod,
	"type":         EntryType,
	"variable":     EntryVariable,
	"var":          EntryVariable,
	"doc":          EntryGuide,
	"term":         EntryWord,
	"protocol":     EntryProtocol,
}

var lineRE = regexp.MustCompile(`(.+?)\s+(\S+)\s+(-?\d+)\s+?(\S*)\s+(.*)`)

func makeEntry(l string) *DocEntry {
	// sqlalchemy.dialects.postgresql.pypostgresql py:module 1 dialects/postgresql.html#$ -
	// dict classes std:term -1 glossary.html#term-dict-classes -
	parts := lineRE.FindStringSubmatch(l)
	name := parts[1]
	path := parts[4]

	var anchor string
	if strings.HasSuffix(path, "#$") {
		anchor = name
		path = path[:len(path)-2]
	} else if strings.Contains(path, "#") {
		ps := strings.Split(path, "#")
		path = strings.TrimSuffix(ps[0], "#")
		anchor = ps[1]
	}

	ts := strings.SplitN(parts[2], ":", 2)

	t := roleToType[ts[len(ts)-1]]
	if t == "" {
		q.Q(l)
		q.Q(parts[1], ts, name)
		panic("unknown role") // TODO: make it a warning
	}

	if parts[5] != "-" {
		name = parts[5]
	}

	return &DocEntry{
		Name:   name,
		Type:   roleToType[ts[len(ts)-1]],
		Path:   path,
		Anchor: anchor,
	}
}

var (
	reProjectName = regexp.MustCompile(`^# Project: (.+)`)
	reVersion     = regexp.MustCompile(`^# Version: (.+)`)
)

// parseHeader parses and validates the header of r.
// It returns a tuple of project name, version, error.
func parseHeader(r *bufio.Reader) (string, string, error) {
	line, err := r.ReadString('\n')
	if err != nil {
		return "", "", err
	}

	if line != "# Sphinx inventory version 2\n" {
		return "", "", errors.New("missing `# Sphinx inventory version 2`")
	}

	line, err = r.ReadString('\n')
	if err != nil {
		return "", "", err
	}

	m := reProjectName.FindStringSubmatch(line)
	if len(m) != 2 {
		return "", "", errors.New("invalid Project line")
	}
	name := m[1]

	line, err = r.ReadString('\n')
	if err != nil {
		return "", "", err
	}

	m = reVersion.FindStringSubmatch(line)
	if len(m) != 2 {
		return "", "", errors.New("invalid Version line")
	}
	version := m[1]

	line, err = r.ReadString('\n')
	if err != nil {
		return "", "", err
	}

	if line != "# The remainder of this file is compressed using zlib.\n" {
		return "", "", errors.New("missing `# The remainder of this file is compressed using zlib.`")
	}

	return name, version, nil
}

// isMine checks whether DirName is in Sphinx format.
func isMine(dirName string) (bool, error) {
	stat, err := os.Stat(path.Join(dirName, "objects.inv"))
	if err != nil {
		if os.IsNotExist(err) {
			return false, nil
		}

		return false, err
	}

	return !stat.IsDir() && stat.Size() > 0, nil
}
