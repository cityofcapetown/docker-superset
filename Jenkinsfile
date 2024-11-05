def label = "superset-${UUID.randomUUID().toString()}"
podTemplate(label: label, yaml: """
    apiVersion: v1
    kind: Pod
    metadata:
        name: ${label}
        annotations:
            container.apparmor.security.beta.kubernetes.io/${label}: unconfined
    labels:
        app: ${label}
    spec:
      containers:
      - name: ${label}
        image: moby/buildkit:v0.9.2-rootless
        imagePullPolicy: IfNotPresent
        command:
        - cat
        tty: true
      - name: kubectl
        image: lachlanevenson/k8s-kubectl:v1.21.10
        imagePullPolicy: IfNotPresent
        command:
        - cat
        tty: true
      nodeSelector:
        workload: batch
    """,
    slaveConnectTimeout: 3600
  ) {
    node(label) {
        stage('setup') {
            git branch: env.BRANCH_NAME, credentialsId: 'jenkins-user', url: 'https://ds1.capetown.gov.za/ds_gitlab/OPM/docker-superset.git'
        }
        stage('image-build') {
            retry(3) {
                container(label) {
                    withCredentials([usernamePassword(credentialsId: 'opm-data-proxy-user', passwordVariable: 'OPM_DATA_PASSWORD', usernameVariable: 'OPM_DATA_USER'),
                                     usernamePassword(credentialsId: 'docker-user', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                        sh '''
                        export SAFE_BRANCH_NAME=$(echo $BRANCH_NAME | sed 's#/#-#g')
                        DOCKER_IMAGE_NAME="superset"
                        ./bin/buildkit-docker.sh ${OPM_DATA_USER} ${OPM_DATA_PASSWORD} \\
                                                 ${DOCKER_USER} ${DOCKER_PASS} \\
                                                 "${PWD}" \\
                                                 "docker.io/cityofcapetown/superset:${SAFE_BRANCH_NAME}"
                        sleep 60
                        '''
                    }
                    updateGitlabCommitStatus name: 'image-build', state: 'success'
                }
            }
        }
        stage('deploy-config') {
            if (env.BRANCH_NAME != 'main') {
                container('kubectl') {
                    sh '''
                    kubectl delete configmap superset-config -n superset-dev
                    kubectl create configmap superset-config -n superset-dev --from-file=${PWD}/configs/superset_config.py
                    '''
                }
                updateGitlabCommitStatus name: 'deploy-config', state: 'success'
            }
        }
        stage('app redeploy') {
            if (env.BRANCH_NAME != 'main') {
                container('kubectl') {
                    sh '''
                    # swap out the docker image tag for the current branch
                    export SAFE_BRANCH_NAME=$(echo $BRANCH_NAME | sed 's#/#-#g')
                    sed -i 's|image: "cityofcapetown/superset:dev"|image: "cityofcapetown/superset:'${SAFE_BRANCH_NAME}'"|g" ${PWD}/k8s/superset-dev.yaml
                    grep "image:" ${PWD}/k8s/superset-dev.yaml

                    kubectl rollout restart statefulset -n superset-dev superset-redis-master superset-postgresql
                    kubectl rollout restart deployment -n superset-dev superset-worker superset superset-celerybeat
                    kubectl rollout status statefulset -n superset-dev superset-redis-master superset-postgresql --timeout=300s
                    kubectl rollout status deployment -n superset-dev superset-worker superset superset-celerybeat --timeout=300s
                    '''
                }
                updateGitlabCommitStatus name: 'deploy', state: 'success'
            }
        }
    }
}