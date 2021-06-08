pipeline {
    agent {
      node {
        label 'py36-terceirizadas'
	    }
    }

    options {
      buildDiscarder(logRotator(numToKeepStr: '5', artifactNumToKeepStr: '5'))
      disableConcurrentBuilds()
      skipDefaultCheckout()
    }

    stages {
        stage('BD') {
        agent {
        label 'master'
        }
        steps {
          script {
            CONTAINER_ID = sh (
            script: 'docker ps -q --filter "name=terceirizadas-db"',
            returnStdout: true
            ).trim()
             if (CONTAINER_ID) {
               sh "echo nome é: ${CONTAINER_ID}"
               sh "docker rm -f ${CONTAINER_ID}"
               sh 'docker run -d --rm --cap-add SYS_TIME --name terceirizadas-db --network python-network -p 5432 -e TZ="America/Sao_Paulo" -e POSTGRES_DB=terceirizadas -e POSTGRES_PASSWORD=adminadmin -e POSTGRES_USER=postgres postgres:9-alpine'
            } else {

                sh 'docker run -d --rm --cap-add SYS_TIME --name terceirizadas-db --network python-network -p 5432 -e TZ="America/Sao_Paulo" -e POSTGRES_DB=terceirizadas -e POSTGRES_PASSWORD=adminadmin -e POSTGRES_USER=postgres postgres:9-alpine'
            }
          }

        }
      }

       stage('CheckOut') {
        steps {
          checkout scm
        }
       }

       stage('Testes') {
        steps {

          sh 'pip install --user pipenv'
          sh 'pipenv install --dev'
          sh 'pipenv run pytest'
          sh 'pipenv run flake8'


        }
        post {
            success{
            //  Publicando arquivo de cobertura
                publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('NEVER_STORE')
            }
       }
      }

    stage('Analise codigo') {
	    when {
           branch 'homolog'
        }
        steps {
            sh 'echo "[ INFO ] Iniciando analise Sonar..." && sonar-scanner \
              -Dsonar.projectKey=SME-Terceirizadas \
              -Dsonar.sources=. \
              -Dsonar.host.url=http://sonar.sme.prefeitura.sp.gov.br \
              -Dsonar.login=0d279825541065cf66a60cbdfe9b8a25ec357226'
        }
    }

       stage('Build DEV') {
         when {
           branch 'development'
         }
        steps {
          sh 'echo build docker image desenvolvimento'
          // Start JOB para build das imagens Docker e push SME Registry
          script {
            step([$class: "RundeckNotifier",
              includeRundeckLogs: true,
              jobId: "f6d90f21-2b9d-40b5-9ca3-b6205f2e3345",
              nodeFilters: "",
              //options: """
              //     PARAM_1=value1
               //    PARAM_2=value2
              //     PARAM_3=
              //     """,
              rundeckInstance: "Rundeck-SME",
              shouldFailTheBuild: true,
              shouldWaitForRundeckJob: true,
              tags: "",
              tailLog: true])
           }
        }
       }

       stage('Deploy DEV') {
         when {
           branch 'development'
         }
        steps {


           //Start JOB de deploy Kubernetes
          sh 'echo Deploy ambiente desenvolvimento'
          script {
            step([$class: "RundeckNotifier",
              includeRundeckLogs: true,
              jobId: "5617fe25-f336-4f63-960d-580510c2ba1f",
              nodeFilters: "",
              //options: """
              //     PARAM_1=value1
               //    PARAM_2=value2
              //     PARAM_3=
              //     """,
              rundeckInstance: "Rundeck-SME",
              shouldFailTheBuild: true,
              shouldWaitForRundeckJob: true,
              tags: "",
              tailLog: true])
          }
        }
       }

       stage('Build HOM') {
         when {
           branch 'homolog'
         }
        steps {

         sh 'echo Deploying ambiente homologacao'

          // Start JOB para build das imagens Docker e push SME Registry

          script {
            step([$class: "RundeckNotifier",
              includeRundeckLogs: true,

              //JOB DE BUILD
              jobId: "744a2c35-d0f9-47f6-bfe4-3176897a670e",
              nodeFilters: "",
              //options: """
              //     PARAM_1=value1
               //    PARAM_2=value2
              //     PARAM_3=
              //     """,
              rundeckInstance: "Rundeck-SME",
              shouldFailTheBuild: true,
              shouldWaitForRundeckJob: true,
              tags: "",
              tailLog: true])
          }
        }
       }

        stage('Deploy HOM') {
         when {
           branch 'homolog'
         }
        steps {
          timeout(time: 24, unit: "HOURS") {
          // telegramSend("${JOB_NAME}...O Build ${BUILD_DISPLAY_NAME} - Requer uma aprovação para deploy !!!\n Consulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)\n")
            input message: 'Deseja realizar o deploy?', ok: 'SIM', submitter: 'marcos_nastri, calvin_rossinhole, ollyver_ottoboni, kelwy_oliveira, pedro_walter, rodolfo_lima, regis_santos, luis_zimmermann, anderson_morais, rodolpho_azeredo'
          }

          script {
            step([$class: "RundeckNotifier",
              includeRundeckLogs: true,
              jobId: "66b30d38-059c-40d3-93d0-1bc83fe5ec9c",
              nodeFilters: "",
              //options: """
              //     PARAM_1=value1
               //    PARAM_2=value2
              //     PARAM_3=
              //     """,
              rundeckInstance: "Rundeck-SME",
              shouldFailTheBuild: true,
              shouldWaitForRundeckJob: true,
              tags: "",
              tailLog: true])
          }
        }
       }

       stage('Build PROD') {
         when {
           branch 'master'
         }
        steps {

            sh 'echo Build image docker Produção'
          // Start JOB para build das imagens Docker e push SME Registry

          script {
            step([$class: "RundeckNotifier",
              includeRundeckLogs: true,

              //JOB DE BUILD
              jobId: "7c4beb8a-4a3a-416c-addb-a6b8dbed08bf",
              nodeFilters: "",
              //options: """
              //     PARAM_1=value1
               //    PARAM_2=value2
              //     PARAM_3=
              //     """,
              rundeckInstance: "Rundeck-SME",
              shouldFailTheBuild: true,
              shouldWaitForRundeckJob: true,
              tags: "",
              tailLog: true])
          }
        }
       }

        stage('Deploy PROD') {
         when {
           branch 'master'
         }
        steps {
          timeout(time: 24, unit: "HOURS") {
          // telegramSend("${JOB_NAME}...O Build ${BUILD_DISPLAY_NAME} - Requer uma aprovação para deploy !!!\n Consulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)\n")
            input message: 'Deseja realizar o deploy?', ok: 'SIM', submitter: 'marcos_nastri, calvin_rossinhole, ollyver_ottoboni, kelwy_oliveira, pedro_walter, rodolfo_lima, regis_santos, anderson_morais'
          }

          script {
            step([$class: "RundeckNotifier",
              includeRundeckLogs: true,
              jobId: "7bdb9dc2-5df6-4725-a134-bf8740b4aaef",
              nodeFilters: "",
              //options: """
              //     PARAM_1=value1
              //    PARAM_2=value2
              //     PARAM_3=
              //     """,
              rundeckInstance: "Rundeck-SME",
              shouldFailTheBuild: true,
              shouldWaitForRundeckJob: true,
              tags: "",
              tailLog: true])
          }
        }
       }
    }

  post {
    always {
      echo 'One way or another, I have finished'
    }
    success {
      telegramSend("${JOB_NAME}...O Build ${BUILD_DISPLAY_NAME} - Esta ok !!!\n Consulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)\n\n Uma nova versão da aplicação esta disponivel!!!")
    }
    unstable {
      telegramSend("O Build ${BUILD_DISPLAY_NAME} <${env.BUILD_URL}> - Esta instavel ...\nConsulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)")
    }
    failure {
      telegramSend("${JOB_NAME}...O Build ${BUILD_DISPLAY_NAME}  - Quebrou. \nConsulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)")
    }
    changed {
      echo 'Things were different before...'
    }
    aborted {
      telegramSend("O Build ${BUILD_DISPLAY_NAME} - Foi abortado.\nConsulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)")
    }
  }
}
