plugins {
    java
    `java-library`
}

allprojects {
    group = "app.thorg.flexmark"
    // Forked from 0.64.8-KMP 0.64.6
    version = "0.1"

    repositories {
        mavenCentral()
    }
}

subprojects {
    apply(plugin = "java-library")

    java {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    tasks.withType<JavaCompile> {
        options.encoding = "UTF-8"
    }

    dependencies {
        testImplementation("junit:junit:4.13.2")
    }
}
