plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark-util"))
    api(project(":flexmark"))

    implementation("org.jetbrains:annotations:24.0.1")

    testImplementation(project(":flexmark-test-util"))
    testImplementation(project(":flexmark-ext-tables"))
    testImplementation(project(":flexmark-core-test"))
}
