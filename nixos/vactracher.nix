{ config, pkgs, lib, ... }:
let cfg = config.services.vactracher;

in {
  options.services.vactracher = with lib; {
    enable = mkEnableOption
      "VactraCHer, the Free and Open Source media streaming server";

    user = mkOption {
      default = "vactracher";
      type = types.str;
      description = "User account under which vactracher runs.";
    };

    dataDir = mkOption {
      default = "/var/lib/${cfg.user}";
      type = types.str;
      description = ''
        Home directory of the VactraCHer user and where its data will be written
        to.
      '';
    };

    envScript = mkOption {
      type = types.str;
      description = "Script to source before starting app";
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.vactracher = {
      description = "VactraCHer Tweeter";
      after = [ "network.target" ];
      requires = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];

      startAt = "hourly";

      environment.STATE_FILE = "${cfg.dataDir}/state_file";

      script = with lib; ''
        source ${cfg.envScript}
        ${pkgs.vactracher}/bin/vactracher
      '';

      serviceConfig.User = cfg.user;
    };

    users.users.vactracher = {
      description = "VactraCHer service user";
      name = cfg.user;
      home = cfg.dataDir;
      createHome = true;
      isSystemUser = true;
    };
  };
}
