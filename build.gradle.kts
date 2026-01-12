plugins {
    java
    `java-library`
}

allprojects {
    group = "com.vladsch.flexmark"
    version = "0.64.8-KMP"

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
