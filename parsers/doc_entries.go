// SPDX-License-Identifier: Apache-2.0

package parsers

// AnchorTmpl is a template string for Dash.app ToC anchors.
const AnchorTmpl = `<a name="//apple_ref/cpp/%s/%s" class="dashAnchor"></a>`

// DocEntry is a documentation entry with a link.
type DocEntry struct {
	Name   string
	Type   DocEntryType
	Path   string
	Anchor string
}

// DocEntryType is one of the pre-defined strings.
// See https://kapeli.com/docsets#supportedentrytypes
// for the official list.
type DocEntryType string

// Entries for DocEntry.Type
const (
	EntryAnnotation  DocEntryType = "Annotation"
	EntryAttribute   DocEntryType = "Attribute"
	EntryBinding     DocEntryType = "Binding"
	EntryBuiltin     DocEntryType = "Builtin"
	EntryCallback    DocEntryType = "Callback"
	EntryCategory    DocEntryType = "Category"
	EntryClass       DocEntryType = "Class"
	EntryCommand     DocEntryType = "Command"
	EntryComponent   DocEntryType = "Component"
	EntryConstant    DocEntryType = "Constant"
	EntryConstructor DocEntryType = "Constructor"
	EntryDefine      DocEntryType = "Define"
	EntryDelegate    DocEntryType = "Delegate"
	EntryDiagram     DocEntryType = "Diagram"
	EntryDirective   DocEntryType = "Directive"
	EntryElement     DocEntryType = "Element"
	EntryEntry       DocEntryType = "Entry"
	EntryEnum        DocEntryType = "Enum"
	EntryEnvironment DocEntryType = "Environment"
	EntryError       DocEntryType = "Error"
	EntryEvent       DocEntryType = "Event"
	EntryException   DocEntryType = "Exception"
	EntryExtension   DocEntryType = "Extension"
	EntryField       DocEntryType = "Field"
	EntryFile        DocEntryType = "File"
	EntryFilter      DocEntryType = "Filter"
	EntryFramework   DocEntryType = "Framework"
	EntryFunction    DocEntryType = "Function"
	EntryGlobal      DocEntryType = "Global"
	EntryGuide       DocEntryType = "Guide"
	EntryHook        DocEntryType = "Hook"
	EntryInstance    DocEntryType = "Instance"
	EntryInstruction DocEntryType = "Instruction"
	EntryInterface   DocEntryType = "Interface"
	EntryKeyword     DocEntryType = "Keyword"
	EntryLibrary     DocEntryType = "Library"
	EntryLiteral     DocEntryType = "Literal"
	EntryMacro       DocEntryType = "Macro"
	EntryMethod      DocEntryType = "Method"
	EntryMixin       DocEntryType = "Mixin"
	EntryModifier    DocEntryType = "Modifier"
	EntryModule      DocEntryType = "Module"
	EntryNamespace   DocEntryType = "Namespace"
	EntryNotation    DocEntryType = "Notation"
	EntryObject      DocEntryType = "Object"
	EntryOperator    DocEntryType = "Operator"
	EntryOption      DocEntryType = "Option"
	EntryPackage     DocEntryType = "Package"
	EntryProtocol    DocEntryType = "Protocol"
	EntryProvider    DocEntryType = "Provider"
	EntryProvisionar DocEntryType = "Provisioner"
	EntryQuery       DocEntryType = "Query"
	EntryRecord      DocEntryType = "Record"
	EntryResource    DocEntryType = "Resource"
	EntrySample      DocEntryType = "Sample"
	EntrySection     DocEntryType = "Section"
	EntryService     DocEntryType = "Service"
	EntrySetting     DocEntryType = "Setting"
	EntryShortcut    DocEntryType = "Shortcut"
	EntryStatement   DocEntryType = "Statement"
	EntryStruct      DocEntryType = "Struct"
	EntryStyle       DocEntryType = "Style"
	EntrySubroutine  DocEntryType = "Subroutine"
	EntryTag         DocEntryType = "Tag"
	EntryTest        DocEntryType = "Test"
	EntryTrait       DocEntryType = "Trait"
	EntryType        DocEntryType = "Type"
	EntryUnion       DocEntryType = "Union"
	EntryValue       DocEntryType = "Value"
	EntryVariable    DocEntryType = "Variable"
	EntryWord        DocEntryType = "Word"
)
