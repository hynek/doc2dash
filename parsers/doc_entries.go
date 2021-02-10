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
type DocEntryType string

const (
	EntryAnnotation  = "Annotation"
	EntryAttribute   = "Attribute"
	EntryBinding     = "Binding"
	EntryBuiltin     = "Builtin"
	EntryCallback    = "Callback"
	EntryCategory    = "Category"
	EntryClass       = "Class"
	EntryCommand     = "Command"
	EntryComponent   = "Component"
	EntryConstant    = "Constant"
	EntryConstructor = "Constructor"
	EntryDefine      = "Define"
	EntryDelegate    = "Delegate"
	EntryDiagram     = "Diagram"
	EntryDirective   = "Directive"
	EntryElement     = "Element"
	EntryEntry       = "Entry"
	EntryEnum        = "Enum"
	EntryEnvironment = "Environment"
	EntryError       = "Error"
	EntryEvent       = "Event"
	EntryException   = "Exception"
	EntryExtension   = "Extension"
	EntryField       = "Field"
	EntryFile        = "File"
	EntryFilter      = "Filter"
	EntryFramework   = "Framework"
	EntryFunction    = "Function"
	EntryGlobal      = "Global"
	EntryGuide       = "Guide"
	EntryHook        = "Hook"
	EntryInstance    = "Instance"
	EntryInstruction = "Instruction"
	EntryInterface   = "Interface"
	EntryKeyword     = "Keyword"
	EntryLibrary     = "Library"
	EntryLiteral     = "Literal"
	EntryMacro       = "Macro"
	EntryMethod      = "Method"
	EntryMixin       = "Mixin"
	EntryModifier    = "Modifier"
	EntryModule      = "Module"
	EntryNamespace   = "Namespace"
	EntryNotation    = "Notation"
	EntryObject      = "Object"
	EntryOperator    = "Operator"
	EntryOption      = "Option"
	EntryPackage     = "Package"
	EntryProtocol    = "Protocol"
	EntryProvider    = "Provider"
	EntryProvisionar = "Provisioner"
	EntryQuery       = "Query"
	EntryRecord      = "Record"
	EntryResource    = "Resource"
	EntrySample      = "Sample"
	EntrySection     = "Section"
	EntryService     = "Service"
	EntrySetting     = "Setting"
	EntryShortcut    = "Shortcut"
	EntryStatement   = "Statement"
	EntryStruct      = "Struct"
	EntryStyle       = "Style"
	EntrySubroutine  = "Subroutine"
	EntryTag         = "Tag"
	EntryTest        = "Test"
	EntryTrait       = "Trait"
	EntryType        = "Type"
	EntryUnion       = "Union"
	EntryValue       = "Value"
	EntryVariable    = "Variable"
	EntryWord        = "Word"
)
