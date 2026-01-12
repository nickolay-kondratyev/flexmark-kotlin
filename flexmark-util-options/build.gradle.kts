plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util-misc"))
    api(project(":flexmark-util-sequence"))
    implementation("org.jetbrains:annotations:24.0.1")
}
