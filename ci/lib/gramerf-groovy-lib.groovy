def restartNode(node_label){

    node ("$node_label") {
        print "Rebooting $node_label........."
        if (isUnix()) {
            sh "sudo shutdown -r +1"
        } else {
            bat "shutdown /r /f"
        }
    }

    print "Waiting for the $node_label to reboot........."
    sleep(time:80,unit:"SECONDS")

    def numberOfAttemps = 0
    while (numberOfAttemps < 20) {
        if(Jenkins.instance.getNode(node_label).toComputer().isOnline()){
            print "Node $node_label is rebooted and ready to use"
            return true;
        }
        print "Waiting for the $node_label to reboot........."
        sleep(time:20,unit:"SECONDS")
        numberOfAttemps += 1
    }
    print "Node $node_label is not up running"
    return false
}

def getNodeName(){

    if (run.contains("ov") || run_specific_perf_test.contains("ov")){
        echo "open vino workload is selected ..."
        return 'graphene_wcity_02'
    } else if (run.contains("redis") || run_specific_perf_test.contains("redis")){
        echo "redis workload is selected ..."
        return 'graphene_perf_redis_taken_out_for_vasanth'
    } else if (run.contains("tf") || run_specific_perf_test.contains("tf")) {
        echo "tensorflow workload is selected ..."
        return 'graphene_wcity_02'
    }

}

def preActions(){

    // there is a bug in the active choice parameter reference variable which adds comma[,] character at the end
    if(build_gramine.endsWith(","))
    {
        build_gramine = build_gramine.substring(0,build_gramine.length() - 1);
    }
    if(gramine_repo_commit_id.endsWith(","))
    {
        gramine_repo_commit_id = gramine_repo_commit_id.substring(0,gramine_repo_commit_id.length() - 1);
    }

}

return this