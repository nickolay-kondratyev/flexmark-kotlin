rootProject.name = "flexmark-kotlin"

// Utility modules (in dependency order)
include("flexmark-util-misc")
include("flexmark-util-visitor")
include("flexmark-util-data")
include("flexmark-util-collection")
include("flexmark-util-sequence")
include("flexmark-util-html")
include("flexmark-util-options")
include("flexmark-util-builder")
include("flexmark-util-dependency")
include("flexmark-util-ast")
include("flexmark-util-format")
include("flexmark-util")

// Core
include("flexmark")

// Test infrastructure
include("flexmark-test-util")
include("flexmark-test-specs")
include("flexmark-core-test")

// Extensions
include("flexmark-ext-tables")
include("flexmark-ext-footnotes")
include("flexmark-ext-yaml-front-matter")
