// Define the heimdallr module
var heimdallrApp = angular.module('heimdallrApp', ['ngAnimate', 'ui.bootstrap']);

function mapID(arr) {
  return arr.map(function(item) {
    return item.id;
  });
}

// Define the KillsController
heimdallrApp.controller('KillsController', function KillsController($scope, $http, $interval, $location) {
  $scope.kms = [];
  $scope.params = {
    "victimCharacter": [],
    "victimCorporation": [],
    "victimAlliance": [],
    "victimShipType": [],
    "victimShipGroup": [],
    "attackerCharacter": [],
    "attackerCorporation": [],
    "attackerAlliance": [],
    "attackerShipType": [],
    "attackerShipGroup": [],
    "carrying": [],
    "solarSystem": [],
    "constellation": [],
    "region": [],
    "minimumValue": null
  };
  $scope.baseParams = JSON.parse(JSON.stringify($scope.params));

  // Take the URL params if there are any
  if($location.path().length > 1) {
    params = JSON.parse(atob($location.path().slice(1)));
    for(var key in params) {
      $scope.params[key] = params[key];
    }
  }

  // Static data for autocompletion
  $scope.ships = [];
  $scope.groups = [];
  $scope.systems = [];
  $scope.constellations = [];
  $scope.regions = [];

  $http.get("/autocomplete/ships")
  .then(function(response) {
    $scope.ships = response.data;
  });

  $http.get("/autocomplete/groups")
  .then(function(response) {
    $scope.groups = response.data;
  });

  $http.get("/map/systems")
  .then(function(response) {
    $scope.systems = response.data;
  });

  $http.get("/map/constellations")
  .then(function(response) {
    $scope.constellations = response.data;
  });

  $http.get("/map/regions")
  .then(function(response) {
    $scope.regions = response.data;
  });

  function paramsToJson(params) {
    params = JSON.parse(JSON.stringify(params));
    ret = {};
    for(var key in params) {
      if(key != "minimumValue") {
        if(params[key].length > 0) {
          ret[key] = mapID(params[key]);
        }
      } else if (params[key] > 0) {
        ret[key] = params[key];
      }
    }
    return ret;
  }

  function paramsToBase64(params) {
    params = JSON.parse(JSON.stringify(params));
    ret = {};
    for(var key in params) {
      if(key != "minimumValue") {
        if(params[key].length > 0) {
          ret[key] = params[key];
        }
      } else if (params[key] > 0) {
        ret[key] = params[key];
      }
    }
    return ret;
  }


  var getData = function() {
    // Prune the param object from objects to ids
    params = paramsToJson($scope.params);

    $http.get("/search/"+btoa(JSON.stringify(params)))
    .then(function(response) {
      //$scope.kms = response.data;
      //Iterate through the response data and add them if they're new
      for(var i = 0; i < response.data.length; i++) {
        found = false;
        for(var ii = 0; ii < $scope.kms.length; ii++) {
          if(response.data[i].killID == $scope.kms[ii].killID) {
            found = true;
          }
        }
        if(found === false) {
          // Push the new object on to the km queue
          response.data[i].killmail.killTime = Date.parse(response.data[i].killmail.killTime);
          $scope.kms.push(response.data[i]);

          // If it's getting too large let's cull an object to avoid memory leaks
          if($scope.kms.length > 150) {
            $scope.kms.shift();
          }
        }
      }
    });
  };

  getData();
  $interval(function() {
    getData();
  }, 10000);


  // Autocomplete Feeds
  $scope.autoCompleteAlliance = function(search) {
    return $http.get("/autocomplete/alliance/"+search)
    .then(function(response) {
      return response.data;
    });
  };

  $scope.autoCompleteCorporation = function(search) {
    return $http.get("/autocomplete/corporation/"+search)
    .then(function(response) {
      return response.data;
    });
  };

  $scope.autoCompleteCharacter = function(search) {
    return $http.get("/autocomplete/character/"+search)
    .then(function(response) {
      return response.data;
    });
  };



  // Update location service with new Filters
  function updateLocation() {
    obj = btoa(JSON.stringify(paramsToBase64($scope.params)));
    $location.path(obj);
  }



  // Manipulate Filters
  // Victim Alliance
  $scope.addVictimAlliance = function(item) {
    if(mapID($scope.params['victimAlliance']).indexOf(item.id) < 0) {
      $scope.params['victimAlliance'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeVictimAlliance = function(item) {
    if(mapID($scope.params['victimAlliance']).indexOf(item.id) > -1) {
      index = mapID($scope.params['victimAlliance']).indexOf(item.id);
      $scope.params['victimAlliance'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };

  // Victim Corporation
  $scope.addVictimCorporation = function(item) {
    if(mapID($scope.params['victimCorporation']).indexOf(item.id) < 0) {
      $scope.params['victimCorporation'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeVictimCorporation = function(item) {
    if(mapID($scope.params['victimCorporation']).indexOf(item.id) > -1) {
      index = mapID($scope.params['victimCorporation']).indexOf(item.id);
      $scope.params['victimCorporation'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };

  // Victim Character
  $scope.addVictimCharacter = function(item) {
    if(mapID($scope.params['victimCharacter']).indexOf(item.id) < 0) {
      $scope.params['victimCharacter'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeVictimCharacter = function(item) {
    if(mapID($scope.params['victimCharacter']).indexOf(item.id) > -1) {
      index = mapID($scope.params['victimCharacter']).indexOf(item.id);
      $scope.params['victimCharacter'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };

  // Victim Ship
  $scope.addVictimShip = function(item) {
    if(mapID($scope.params['victimShipType']).indexOf(item.id) < 0) {
      $scope.params['victimShipType'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeVictimShip = function(item) {
    if(mapID($scope.params['victimShipType']).indexOf(item.id) > -1) {
      index = mapID($scope.params['victimShipType']).indexOf(item.id);
      $scope.params['victimShipType'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };

  // Victim Group
  $scope.addVictimGroup = function(item) {
    if(mapID($scope.params['victimShipGroup']).indexOf(item.id) < 0) {
      $scope.params['victimShipGroup'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeVictimGroup = function(item) {
    if(mapID($scope.params['victimShipGroup']).indexOf(item.id) > -1) {
      index = mapID($scope.params['victimShipGroup']).indexOf(item.id);
      $scope.params['victimShipGroup'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };

  // Attacker Alliance
  $scope.addAttackerAlliance = function(item) {
    if(mapID($scope.params['attackerAlliance']).indexOf(item.id) < 0) {
      $scope.params['attackerAlliance'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeAttackerAlliance = function(item) {
    if(mapID($scope.params['attackerAlliance']).indexOf(item.id) > -1) {
      index = mapID($scope.params['attackerAlliance']).indexOf(item.id);
      $scope.params['attackerAlliance'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };

  // Attacker Corporation
  $scope.addAttackerCorporation = function(item) {
    if(mapID($scope.params['attackerCorporation']).indexOf(item.id) < 0) {
      $scope.params['attackerCorporation'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeAttackerCorporation = function(item) {
    if(mapID($scope.params['attackerCorporation']).indexOf(item.id) > -1) {
      index = mapID($scope.params['attackerCorporation']).indexOf(item.id);
      $scope.params['attackerCorporation'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };

  // Attacker Character
  $scope.addAttackerCharacter = function(item) {
    if(mapID($scope.params['attackerCharacter']).indexOf(item.id) < 0) {
      $scope.params['attackerCharacter'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeAttackerCharacter = function(item) {
    if(mapID($scope.params['attackerCharacter']).indexOf(item.id) > -1) {
      index = mapID($scope.params['attackerCharacter']).indexOf(item.id);
      $scope.params['attackerCharacter'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };

  // Attacker Ship
  $scope.addAttackerShip = function(item) {
    if(mapID($scope.params['attackerShipType']).indexOf(item.id) < 0) {
      $scope.params['attackerShipType'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeAttackerShip = function(item) {
    if(mapID($scope.params['attackerShipType']).indexOf(item.id) > -1) {
      index = mapID($scope.params['attackerShipType']).indexOf(item.id);
      $scope.params['attackerShipType'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };

  // Attacker Group
  $scope.addAttackerGroup = function(item) {
    if(mapID($scope.params['attackerShipGroup']).indexOf(item.id) < 0) {
      $scope.params['attackerShipGroup'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeAttackerGroup = function(item) {
    if(mapID($scope.params['attackerShipGroup']).indexOf(item.id) > -1) {
      index = mapID($scope.params['attackerShipGroup']).indexOf(item.id);
      $scope.params['attackerShipGroup'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  }

  // System
  $scope.addSystem = function(item) {
    if(mapID($scope.params['solarSystem']).indexOf(item.id) < 0) {
      $scope.params['solarSystem'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeSystem = function(item) {
    if(mapID($scope.params['solarSystem']).indexOf(item.id) > -1) {
      index = mapID($scope.params['solarSystem']).indexOf(item.id);
      $scope.params['solarSystem'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  }

  // Constellation
  $scope.addConstellation = function(item) {
    if(mapID($scope.params['constellation']).indexOf(item.id) < 0) {
      $scope.params['constellation'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeConstellation = function(item) {
    if(mapID($scope.params['constellation']).indexOf(item.id) > -1) {
      index = mapID($scope.params['constellation']).indexOf(item.id);
      $scope.params['constellation'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  }

  // Region
  $scope.addRegion = function(item) {
    if(mapID($scope.params['region']).indexOf(item.id) < 0) {
      $scope.params['region'].push(item);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };
  $scope.removeRegion = function(item) {
    if(mapID($scope.params['region']).indexOf(item.id) > -1) {
      index = mapID($scope.params['region']).indexOf(item.id);
      $scope.params['region'].splice(index, 1);
      $scope.kms = [];
      getData();
      updateLocation();
    }
  }


  $scope.resetFilters = function() {
    if(JSON.stringify($scope.params) !== JSON.stringify($scope.baseParams)) {
      $scope.params = JSON.parse(JSON.stringify($scope.baseParams));
      $scope.kms = [];
      getData();
      updateLocation();
    }
  };




  // Click functions
  // Add Victim
  $scope.addVictim = function(item) {
    // Check if we have an alliance, otherwise just use the corporation
    if("alliance" in item.killmail.victim) {
      $scope.addVictimAlliance(item.killmail.victim.alliance);
    } else {
      $scope.addVictimCorporation(item.killmail.victim.corporation);
    }
  }

  // Add Attacker
  $scope.addAttacker = function(item) {
    // Check if we have an alliance, otherwise just use the corporation
    if("alliance" in item.killmail.finalBlow) {
      $scope.addAttackerAlliance(item.killmail.finalBlow.alliance);
    } else {
      $scope.addAttackerCorporation(item.killmail.finalBlow.corporation);
    }
  }




  // Lookup functions
  // System
  $scope.getSystem = function(id) {
    for(var i = 0; i < $scope.systems.length; i++) {
      if($scope.systems[i].id == id) {
        return $scope.systems[i];
      }
    }
    return null;
  }

  // Region
  $scope.getRegion = function(id) {
    for(var i = 0; i < $scope.regions.length; i++) {
      if($scope.regions[i].id == id) {
        return $scope.regions[i];
      }
    }
    return null;
  }

  // Ship Type
  $scope.getShipType = function(id) {
    for(var i = 0; i < $scope.ships.length; i++) {
      if($scope.ships[i].id == id) {
        return $scope.ships[i];
      }
    }
    return null;
  }




  // Display functions
  $scope.iskFormat = function(isk) {
    return numeral(isk).format('0,0.00a');
  };

  $scope.sysSecStatus = function(sec) {
    if(sec > 0 && sec <= 0.05) {
      return 0.1;
    } else {
      return numeral(sec).format('0.0');
    }
  };

  $scope.sysSecClass = function(sec) {
    if(sec > 0 && sec <= 0.05) {
      return "sec-0-1";
    } else {
      sec = Math.round(sec * 10) / 10;
      if(sec <= 0) {
        return "sec-0-0";
      } else {
        return "sec-" + numeral(sec).format('0.0').replace(".", "-");
      }
    }
  };

  $scope.victimIcon = function(k) {
    // Check if we have an alliance, otherwise just use the corporation
    if("alliance" in k.killmail.victim) {
      return "https://imageserver.eveonline.com/Alliance/"+k.killmail.victim.alliance.id+"_64.png";
    } else {
      return "https://imageserver.eveonline.com/Corporation/"+k.killmail.victim.corporation.id+"_64.png";
    }
  };

  $scope.victimName = function(k) {
    // Check if we have a character, otherwise just the corporation
    if("character" in k.killmail.victim) {
      return k.killmail.victim.character.name;
    } else {
      return k.killmail.victim.corporation.name;
    }
  };

  $scope.victimGuild = function(k) {
    r = k.killmail.victim.corporation.name;
    if("alliance" in k.killmail.victim) {
      r = r + " / " + k.killmail.victim.alliance.name;
    }
    return r;
  };

  $scope.finalBlowIcon = function(k) {
    // Check if we have an alliance otherwise, just use the corporation
    if("alliance" in k.killmail.finalBlow) {
      return "https://imageserver.eveonline.com/Alliance/"+k.killmail.finalBlow.alliance.id+"_64.png";
    } else if("corporation" in k.killmail.finalBlow) {
      return "https://imageserver.eveonline.com/Corporation/"+k.killmail.finalBlow.corporation.id+"_64.png";
    } else {
      return "/static/img/eve-question.png"
    }
  };

  $scope.finalBlowName = function(k) {
    // Check if we have a character, otherwise just the corporation
    if("character" in k.killmail.finalBlow) {
      return k.killmail.finalBlow.character.name;
    } else if("corporation" in k.killmail.finalBlow) {
      return k.killmail.finalBlow.corporation.name;
    } else {
      return "?"
    }
  };

  $scope.finalBlowGuild = function(k) {
    r = ""
    if("corporation" in k.killmail.finalBlow) {
      r = r + k.killmail.finalBlow.corporation.name;
    }
    if("alliance" in k.killmail.finalBlow) {
      r = r + " / " + k.killmail.finalBlow.alliance.name;
    }
    if(r == "") {
      r = "?"
    }
    return r;
  };
});
