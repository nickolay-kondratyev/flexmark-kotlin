plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-data"))
    api(project(":flexmark-util-ast"))
    api(project(":flexmark-util-format"))
    api(project(":flexmark-util-sequence"))
    api("junit:junit:4.13.2")
    implementation("org.jetbrains:annotations:24.0.1")
}
