plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-collection"))
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-data"))
    implementation("org.jetbrains:annotations:24.0.1")
}
