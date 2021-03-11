// SPDX-License-Identifier: Apache-2.0

package doc2dash

import (
	"database/sql"
	"fmt"
	"path/filepath"
	"strings"

	"github.com/hynek/doc2dash/parsers"
	_ "github.com/mattn/go-sqlite3" // sql needs import side-effects
)

const (
	initSQL = `
CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);
CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);
`
	insertSQL            = `INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?);`
	filesSQL             = `SELECT DISTINCT iif(like("%#%", path), substr(path, 0, instr(path, "#")), path) FROM searchIndex;`
	docEntriesForFileSQL = `SELECT name, type, path FROM searchIndex WHERE path LIKE ? || '#%'`
)

// IndexDB is a database that holds the search index.
type IndexDB struct {
	db            *sql.DB
	insertStmt    *sql.Stmt
	deForFileStmt *sql.Stmt
}

// InitIndexDB initializes the index database and returns a handle to it.
func InitIndexDB(path string) (*IndexDB, error) {
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		return nil, err
	}

	_, err = db.Exec(initSQL)
	if err != nil {
		return nil, fmt.Errorf("can't initialize index database: %w", err)
	}

	stmt, err := db.Prepare(insertSQL)
	if err != nil {
		return nil, fmt.Errorf("could not prepare insert statement: %w", err)
	}

	qStmt, err := db.Prepare(docEntriesForFileSQL)
	if err != nil {
		return nil, fmt.Errorf("could not prepare query statement: %w", err)
	}

	return &IndexDB{db, stmt, qStmt}, nil
}

// AddDocEntry adds de to the index db.
func (idb *IndexDB) AddDocEntry(de *parsers.DocEntry) error {
	path := de.Path
	if de.Anchor != "" {
		path = path + "#" + de.Anchor
	}

	_, err := idb.insertStmt.Exec(de.Name, de.Type, path)

	return err
}

// DocEntriesForFile returns a lookup table DocEntry.Name to DocEntry.
func (idb *IndexDB) DocEntriesForFile(
	filePath string,
) (map[string]parsers.DocEntry, error) {
	lt := make(map[string]parsers.DocEntry)

	// q.Q(filepath.Base(filePath))
	rows, err := idb.deForFileStmt.Query(filepath.Base(filePath))
	if err != nil {
		return nil, fmt.Errorf("could not retrieve list of doc entries for file: %w", err)
	}
	defer rows.Close()

	var name, typ, pathWithAnchor string
	for rows.Next() {
		err = rows.Scan(&name, &typ, &pathWithAnchor)
		if err != nil {
			return nil, err
		}

		// q.Q(name, typ, p)
		parts := strings.Split(pathWithAnchor, "#")
		p := parts[0]

		var anchor string
		if len(parts) > 1 {
			anchor = parts[1]
		}

		de := parsers.DocEntry{Name: name, Type: parsers.DocEntryType(typ), Path: p, Anchor: anchor}

		lt["#"+de.Anchor] = de
		lt[pathWithAnchor] = de
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("could not retrieve list of indexed files: %w", err)
	}

	return lt, nil
}

// IndexedFiles returns a slice of paths that contain DocEntrys.
func (idb *IndexDB) IndexedFiles() ([]string, error) {
	paths := make([]string, 0, 128)

	rows, err := idb.db.Query(filesSQL)
	if err != nil {
		return nil, fmt.Errorf("could not retrieve list of indexed files: %w", err)
	}
	defer rows.Close()

	var path string
	for rows.Next() {
		err = rows.Scan(&path)
		if err != nil {
			return nil, err
		}
		paths = append(paths, strings.Split(path, "#")[0])
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("could not retrieve list of indexed files: %w", err)
	}

	return paths, nil
}

// Close closes all resources.
func (idb *IndexDB) Close() {
	idb.insertStmt.Close()
	idb.db.Close()
}

// MakeLookupTable returns a map from DocEntry.Name to *DocEntry.
// func MakeLookupTable(des []parsers.DocEntry) map[string]*parsers.DocEntry {
// 	lt := make(map[string]*parsers.DocEntry)
// 	for _, de := range des {
// 		lt[de.Name] = &de
// 	}

// 	return lt, nil
// }
