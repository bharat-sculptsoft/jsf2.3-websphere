import sys
import getopt
import time
import traceback

host = r"localhost"
cell = r""
cluster = r""
server = r"server1"
webservers = r""
node = r"DESKTOP-DC0UL6INode01"
applicationName = r"jsf-webs-new-0.0.1-SNAPSHOT"
contextRoot = r"/jsf-webs-new"
virtualHost = r"default_host"
sharedLibs = r""
parentLast = r"true"
webModuleParentLast = r"false"
packageFile = r"D:\jsf-workspace\jsf-webs-new\target\jsf-webs-new-0.0.1-SNAPSHOT.war"
restartAfterDeploy = r"true"
deployOptions = r""


class WebSphere:
    def listApplications(self):
        print "[LIST APPLICATIONS]", host
        print time.strftime("%Y-%b-%d %H:%M:%S %Z")
        print AdminApp.list()

    def restartServer(self):
        print '-' * 60
        print "[RESTARTING SERVER]", host
        print time.strftime("%Y-%b-%d %H:%M:%S %Z")
        print '-' * 60
        try:
            if "" != cluster:
                appManager = AdminControl.queryNames('name=' + cluster + ',type=Cluster,process=dmgr,*')
                print AdminControl.invoke(appManager, 'rippleStart')
                print ""
                print '=' * 60
                print "[NOTICE]: It takes a few minutes for the cluster to fully back running after the build finished!"
                print '=' * 60
                print ""
            elif "" != node:
                appManager = AdminControl.queryNames('node=' + node + ',type=Server,process=' + server + ',*')
                print AdminControl.invoke(appManager, 'restart')
            else:
                appManager = AdminControl.queryNames('type=Server,process=' + server + ',*')
                print AdminControl.invoke(appManager, 'restart')
        except:
            print "FAILED to restart cluster/server:"
            print '-' * 10
            traceback.print_exc(file=sys.stdout)
            print '-' * 10
            print "try to startApplication directly..."
            self.startApplication()

    def startApplication(self):
        print '-' * 60
        print "[STARTING APPLICATION]", host, applicationName
        print time.strftime("%Y-%b-%d %H:%M:%S %Z")
        print '-' * 60
        try:
            if "" != cluster:
                print AdminApplication.startApplicationOnCluster(applicationName, cluster)
            elif "" != node:
                appManager = AdminControl.queryNames('node=' + node + ',type=ApplicationManager,process=' + server + ',*')
                print AdminControl.invoke(appManager, 'startApplication', applicationName)
            else:
                appManager = AdminControl.queryNames('type=ApplicationManager,process=' + server + ',*')
                print AdminControl.invoke(appManager, 'startApplication', applicationName)
        except:
            print "FAILED to start application:"
            print '-' * 10
            traceback.print_exc(file=sys.stdout)
            print '-' * 10
            raise

    def stopApplication(self):
        print '-' * 60
        print "[STOPPING APPLICATION]", host, applicationName
        print time.strftime("%Y-%b-%d %H:%M:%S %Z")
        print '-' * 60
        try:
            if "" != cluster:
                print AdminApplication.stopApplicationOnCluster(applicationName, cluster)
            elif "" != node:
                appManager = AdminControl.queryNames('node=' + node + ',type=ApplicationManager,process=' + server + ',*')
                print AdminControl.invoke(appManager, 'stopApplication', applicationName)
            else:
                appManager = AdminControl.queryNames('type=ApplicationManager,process=' + server + ',*')
                print AdminControl.invoke(appManager, 'stopApplication', applicationName)
        except:
            print "FAILED to stop application:"
            print '-' * 10
            traceback.print_exc(file=sys.stdout)
            print '-' * 10
            raise

    def installApplication(self):
        print '-' * 60
        print "[INSTALLING APPLICATION]", host, applicationName
        print time.strftime("%Y-%b-%d %H:%M:%S %Z")
        print '-' * 60

        options = ['-distributeApp', '-appname', applicationName]
        if "" != deployOptions:
            options[:0] = deployOptions.split()

        try:
            if "" != cluster:
                serverMapping = 'WebSphere:cluster=' + cluster
                if "" != webservers:
                    for webserver in webservers.split(','):
                        serverMapping += '+WebSphere:server=' + webserver.strip()
                options += ['-cluster', cluster, '-MapModulesToServers', [['.*', '.*', serverMapping]]]
            else:
                serverMapping = 'WebSphere:server=' + server
                options += ['-MapModulesToServers', [['.*', '.*', serverMapping]]]

            if "" != contextRoot:
                options += ['-contextroot', contextRoot]

            if "" != virtualHost:
                options += ['-MapWebModToVH', [['.*', '.*', virtualHost]]]

            if "" != sharedLibs:
                libs = []
                for lib in sharedLibs.split(','):
                    libs.append(['.*', '.*', lib])
                options += ['-MapSharedLibForMod', libs]

            print ""
            print "options: ", options
            print ""

            print "INSTALLING"
            print AdminApp.install(packageFile, options)

            self.__modifyClassloader()

            print "SAVING CONFIG"
            AdminConfig.save()

            if "" != cluster:
                print "SYNCING"
                AdminNodeManagement.syncActiveNodes()

            result = AdminApp.isAppReady(applicationName)
            while result == "false":
                print "STATUS:", AdminApp.getDeployStatus(applicationName)
                time.sleep(5)
                result = AdminApp.isAppReady(applicationName)
            print "INSTALLED", applicationName
        except:
            print "FAILED to install application: ", applicationName
            print '-' * 10
            traceback.print_exc(file=sys.stdout)
            print '-' * 10
            raise

    def __modifyClassloader(self):
        deployments = AdminConfig.getid("/Deployment:" + applicationName + "/")
        deploymentObject = AdminConfig.showAttribute(deployments, "deployedObject")

        if "true" == parentLast:
            # AdminApplication.configureClassLoaderLoadingModeForAnApplication(applicationName, "PARENT_LAST")
            classloader = AdminConfig.showAttribute(deploymentObject, "classloader")
            AdminConfig.modify(classloader, [['mode', 'PARENT_LAST']])

        if "true" == webModuleParentLast:
            modules = AdminConfig.showAttribute(deploymentObject, "modules")
            arrayModules = modules[1:len(modules) - 1].split(" ")
            for module in arrayModules:
                if module.find('WebModuleDeployment') != -1:
                    AdminConfig.modify(module, [['classloaderMode', 'PARENT_LAST']])

    def uninstallApplication(self):
        print '-' * 60
        print "[UNINSTALLING APPLICATION]", host, applicationName
        print time.strftime("%Y-%b-%d %H:%M:%S %Z")
        print '-' * 60
        try:
            print AdminApp.uninstall(applicationName)
            AdminConfig.save()
            if "" != cluster:
                AdminNodeManagement.syncActiveNodes()
        except:
            print "FAILED to uninstall application: ", applicationName
            print '-' * 10
            traceback.print_exc(file=sys.stdout)
            print '-' * 10
            raise

    def isApplicationInstalled(self):
        return AdminApplication.checkIfAppExists(applicationName)

    def deploy(self):
        if "true" == self.isApplicationInstalled():
            self.uninstallApplication()

        self.installApplication()
        if "true" == restartAfterDeploy:
            self.restartServer()
        else:
            print "Starting application instead of restarting server..."
            self.startApplication()

        print '-' * 60
        print "[FINISHED]", host, applicationName
        print time.strftime("%Y-%b-%d %H:%M:%S %Z")
        print '-' * 60

# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------

if __name__ == "__main__":
    methods, args = getopt.getopt(sys.argv, 'o:')
    for name, method in methods:
        if name == "-o":
            getattr(WebSphere(), method)()
