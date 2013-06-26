group edgerouters {
    peer-as 12345;
    local-as 65501;
    hold-time 3600;
    router-id ${ip};
    local-address ${ip};
    graceful-restart 1200;

    md5 'bgp_key_here';
    static {
    %for b in blocked_v4:
            route ${b.ip}           next-hop 192.168.127.1 community [ no-export ];
    %endfor
    %for b in blocked_v6:
            route ${b.ip}/128       next-hop 2001:DB8::DEAD:BEEF community [ no-export ];
    %endfor
    }

    process ipblocker-dynamic {
        run /home/ipbbgp/ipblocker_env/bin/ipblocker-exabgp-loop;
    }

    neighbor 1.2.3.1 {
        description "edge-1";
    }
    neighbor 1.2.3.2 {
        description "edge-2";
    }

}
