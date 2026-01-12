plugins {
    `java-library`
}

dependencies {
    api(project(":flexmark"))
    api(project(":flexmark-util"))
    api(project(":flexmark-test-util"))
    api(project(":flexmark-test-specs"))

    implementation("org.jetbrains:annotations:24.0.1")

    testImplementation("org.openjdk.jmh:jmh-core:1.13")
    testImplementation("org.openjdk.jmh:jmh-generator-annprocess:1.13")
}
