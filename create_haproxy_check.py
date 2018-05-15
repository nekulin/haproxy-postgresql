#! /usr/bin/env python

import config
import os
import stat
import string
import sys

BASEDIR = "configs"

APPLICATION_PATH = "."

def utf8len(s):
    return len(s.encode('utf-8'))

def help_exit(exit_status):
    if exit_status is not 0:
        print("Error: Wrong arguments in call")
    help_msg = """Usage:

    %s <project>

    Options:
        project     project name
    """ % sys.argv[0]
    print(help_msg)
    sys.exit(exit_status)

def replace(source_name, props, output_name):
    output = open(output_name, 'w')
    source = open(source_name, 'r')
    for line in source:
        newline = line
        for prop in props:
            newline = newline.replace(prop, props[prop])
        output.write(newline)
    output.close()
    source.close()

def new_haproxy_conf(props):
    project = props["<%= @bn.project %>"]
    new_conf = "%s/%s/haproxy-%s.cnf" % (BASEDIR, project, project)
    print("Creating %s" % new_conf)
    replace("template/haproxy.template", props, new_conf)

def add_hba_checkuser(props):
    print('')
    print("Add the following lines to pg_hba.conf:")
    print("# special loadbalancer account in trust")
    print("host    template1             %s             %s/32        trust" % (props["<%= @bn.checkuser %>"], props["<%= @bn.vipip %>"]))
    print("host    template1             %s             %s/32        trust" % (props["<%= @bn.checkuser %>"], props["<%= @bn.masterdsn %>"].split(':')[0]))
    print("host    template1             %s             %s/32        trust" % (props["<%= @bn.checkuser %>"], props["<%= @bn.standbydsn %>"].split(':')[0]))
    print('')

def add_hba_repmgr(props):
    print('')
    print("Add the following lines to pg_hba.conf:")
    print("# repmgr account")
    print("local   replication   repmgr                            trust")
    print("host    replication   repmgr      127.0.0.1/32          trust")
    print("host    replication   repmgr      %s/32     trust" % props["<%= @bn.masterdsn %>"].split(':')[0])
    print("host    replication   repmgr      %s/32     trust" % props["<%= @bn.standbydsn %>"].split(':')[0])
    
    print("local   repmgr        repmgr                            trust")
    print("host    repmgr        repmgr      127.0.0.1/32          trust")
    print("host    repmgr        repmgr      %s/32     trust" % props["<%= @bn.masterdsn %>"].split(':')[0])
    print("host    repmgr        repmgr      %s/32     trust" % props["<%= @bn.standbydsn %>"].split(':')[0])
    print('')

def main():
    args = len(sys.argv)
    if args is 3:
        if sys.argv[1] == "help":
            help_exit(0)
        else:
            help_exit(1)
    if args is not 2:
        help_exit(1)

    mastername = config.BN_MASTER_NAME
    masterdsn = config.BN_MASTER_DSN
    standbyname = config.BN_STANDBY_NAME
    standbydsn = config.BN_STANDBY_DSN
    checkport = config.BN_CHECK_PORT
    checkuser = config.BN_CHECK_USER
    listenport = config.BN_LISTEN_PORT
    statsuser = config.BN_STATS_USER
    statspassword = config.BN_STATS_PASSWORD
    vipip = config.BN_VIP_IP

    d = utf8len(checkuser) + 33 + 1;
    #print("D %s" % d)
    #print("H %s" % hex(d).split('x')[-1])

    

    # the props
    props = {
        "<%= @bn.project %>": sys.argv[1],
        "<%= @bn.mastername %>": mastername,
        "<%= @bn.standbyname %>": standbyname,
        "<%= @bn.masterdsn %>": masterdsn,
        "<%= @bn.standbydsn %>": standbydsn,
        "<%= @bn.checkport %>": checkport,
        "<%= @bn.stats_user %>": statsuser,
        "<%= @bn.stats_password %>": statspassword,
        "<%= @bn.checkuser %>": checkuser,
        "<%= @bn.checkuserlen %>": str(utf8len(checkuser)+1),
        "<%= @bn.totalsize %>": str(d),
        "<%= @bn.vipip %>": vipip,
        "<%= @bn.totalbytes %>": str(hex(d).split('x')[-1]),
        "<%= @bn.path %>": APPLICATION_PATH
    }

    project = props["<%= @bn.project %>"]
    os.mkdir('%s/%s' % (BASEDIR, project))
    print("Creating haproxy project %s" % (project))
    new_haproxy_conf(props)
    add_hba_checkuser(props)
    add_hba_repmgr(props)

print("Done!")

if __name__ == '__main__':
    main()