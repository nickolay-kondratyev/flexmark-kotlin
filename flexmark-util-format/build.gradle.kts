plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-ast"))
    api(project(":flexmark-util-collection"))
    api(project(":flexmark-util-data"))
    api(project(":flexmark-util-html"))
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-sequence"))
    implementation("org.jetbrains:annotations:24.0.1")
}
