package doc2dash

import (
	"database/sql"
	"fmt"

	"github.com/hynek/doc2dash/parsers"
	_ "github.com/mattn/go-sqlite3" // sql needs import side-effects
)

const (
	initSQL = `
CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);
CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);
`
	insertSQL = `INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?);`
)

// IndexDB is a database that holds the search index.
type IndexDB struct {
	db         *sql.DB
	insertStmt *sql.Stmt
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

	return &IndexDB{db, stmt}, nil
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

func (idb *IndexDB) IndexedFiles() ([]string, error) {
	// select distinct path
}

// Close closes all resources.
func (idb *IndexDB) Close() {
	idb.insertStmt.Close()
	idb.db.Close()
}
