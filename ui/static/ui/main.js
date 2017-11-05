let final_topology = {};

let getCurrentData = function(id, callback) {
  let xhr = new XMLHttpRequest();

  xhr.onload = function () {
    let response = JSON.parse(this.responseText);
    //console.log(response);
    callback([response.time, response.power]);
  };

  xhr.open('GET', 'current_data/' + id + '/');
  xhr.send();
};

let getDataRange = function(ids, start, end, callback) {
  let xhr = new XMLHttpRequest();

  xhr.onload = function () {
    let response = JSON.parse(this.responseText);
    //console.log(response);

    let points = [];
    let node_len = response.length;

    // TODO make this better
    // create the main points
    for (let n in response) {

      for (let p in response[n]) {

        //console.log(response[n][p]);
        let new_point = [response[n][p]["time"]];

        for (let i in node_len) {
          new_point.push(null);
        }

        new_point[parseInt(n) + 1] = response[n][p]["power"];
        points.push(new_point);
      }
    }

    mapped_points = {}
    //console.log(points);

    // fix duplicate timestamps
    for (let i in points) {
      if (!mapped_points[points[i][0]]) {
        mapped_points[points[i][0]] = []
        for (let j in node_len) {
          if (j == 0) {
            continue;
          }
          mapped_points[points[i][0]].push(null);
        }
      }

      for (let j in points[i]) {
        if (j == 0) {
          continue;
        }
        let p = points[i][j];
        if (p != null) {
          mapped_points[points[i][0]][j - 1] = p
        }
      }
    }

    //console.log(mapped_points);

    // turn map to array
    let final_arr = [];
    for (let i in mapped_points) {
      let arr = [parseFloat(i)];
      for (let j in mapped_points[i]) {
        arr.push(mapped_points[i][j]);
      }
      final_arr.push(arr);
    }

    // sort everything (timestamp is 0th index)
    final_arr.sort(function(a, b) {
      return a[0] - b[0];
    });

    //console.log(final_arr);

    callback(final_arr);
  };

  let idsString = '';
  for (i in ids) {
    idsString += '?id=' + ids[i] + '&';
  }

  xhr.open('GET', 'data_range/' + start + '/' + end + '/' + idsString);
  xhr.send();
};

let getTopology = function(callback) {
  let xhr = new XMLHttpRequest();

  xhr.onload = function () {
    console.log(this.responseText);
    let response = JSON.parse(this.responseText);
    console.log(response);
    callback(response);
  };

  xhr.open('GET', 'topology/');
  xhr.send();
};

let getDevices = function(callback) {
  let xhr = new XMLHttpRequest();

  xhr.onload = function () {
    //console.log(this.responseText);
    let response = JSON.parse(this.responseText);
    callback(response);
  };

  xhr.open('GET', 'devices/');
  xhr.send();
};

let getDrivers = function(callback) {
  let xhr = new XMLHttpRequest();

  xhr.onload = function () {
    console.log(this.responseText);
    let response = JSON.parse(this.responseText);
    callback(response);
  };

  xhr.open('GET', 'drivers/');
  xhr.send();
};

let transformTopology = function(topology) {
  let chartConfig = {
    chart: {
      container: '#nodes',
      rootOrientation: 'WEST',
      connectors: {
        type: 'step',
      },
      node: {
        HTMLclass: "node-context-menu"
      }
    }
  };

  // convert flat tree to tree with children
  let node_list = {}

  for (let i in topology) {
    if (!topology[i].children) {
      topology[i].children = [];
    }

    node_list[topology[i]['node_id']] = topology[i];
    if (topology[i]['parent_id'] != topology[i]['node_id']) {
      node_list[topology[i]['parent_id']].children.push(node_list[topology[i]['node_id']])
    }
  }

  // find the root in possibly unordered list / dictionary
  let root = {}

  for (let i in node_list) {
    if (node_list[i]['node_id'] == 0) {
      root = node_list[i];
      break;
    }
  }

  // generate the nodeStructure
  let getNode = function(node) {
    if (!node['devices']) {
      return {};
    }

    let arr = []
    for (let i in node.children) {
      arr.push(getNode(node.children[i]));
    }
    devices = ''

    for (let i in node['devices']) {
      if (i != 0) {
        devices += ', '
      }

      devices += node['devices'][i]['description'];
    }

    if (node['devices'].length != 0) {
      devices = ' (' + devices + ')';
    }

    return {
      text: {name: node['description'] + devices},
      HTMLid: 'node-' + node['node_id'],
      children: arr
    }
  }

  chartConfig["root"] = root;
  chartConfig["nodeStructure"] = getNode(root);

  return chartConfig
}


window.onload = function () {
  generateTopology();

  var menu = [{
    name: 'Add Device',
    fun: function (data, e) {
    }
  }, {
    name: 'Add Branch',
    fun: function (data, e) {
    }
  }, {
    name: 'Edit Node',
    fun: function (data, e) {
      console.log(this);
      console.log(data);
      console.log(e);
    }
  }, {
    name: 'Remove Branch',
    fun: function (data, e) {
      // TODO add warning that it will remove all child branches
    }
  }];

  $.contextMenu({
    selector: '.node-context-menu',
    callback: function(key, options) {
      // TODO
      let id = options["$trigger"][0].id;
      let node_id = id.replace("node-", "");
      switch (key) {
        case 'addbranch':
          break;
        case 'adddevice':
          break;
        case 'edit':
          break;
        case 'remove':
          break;
      }
    },
    items: {
      'addbranch': {name: 'Add Device'},
      'adddeveice': {name: 'Add Branch'},
      'edit': {name: 'Edit Node'},
      'remove': {name: 'Remove Branch'}
    }
  });

  getDrivers((drivers) => {
    for (let i in drivers) {
      let tr = document.createElement('tr');
      let t1 = document.createElement('td');
      let t2 = document.createElement('td');
      let t3 = document.createElement('td');
      let btn = document.createElement('button');
      btn.dataset['driver_id'] = drivers[i]['driver_id'];
      btn.classList.add('ui');
      btn.classList.add('primary');
      btn.classList.add('button');
      btn.classList.add('add-device');
      btn.textContent = 'Add Device';
      t3.appendChild(btn);
      t1.textContent = drivers[i]["name"];
      t2.textContent = drivers[i]["driver_description"];
      tr.appendChild(t1);
      tr.appendChild(t2);
      tr.appendChild(t3);
      document.getElementById('drivers').appendChild(tr);
    }
  });

  $('body').on('click', '.node-context-menu', function () {
    // TODO get data attribute working.
    let node_id = this.id.replace("node-", "");
    let node = final_topology[node_id];
    mainChart.start(node);
  });

  $('body').on('click', '.add-device', function () {
    let form = document.getElementById('add-device-form');
    form.reset();
    document.getElementById('add-device-driver').value = this.dataset['driver_id']
    $('#add-device').modal('show');
  });

  $('body').on('click', '#add-device-submit', function () {
    let submit = document.getElementById('add-device-submit');
    submit.classList.add('loading');

    let form = document.getElementById('add-device-form');
    let xhr = new XMLHttpRequest();

    xhr.onload = function () {
      submit.classList.remove('loading');
      $('#add-device').modal('hide');
      let response = JSON.parse(this.responseText);
      console.log(response);
      // TODO check response for success and fail
      generateTopology();
    };

    xhr.open('POST', 'device/');
    xhr.send(new FormData(form));
  });
}

var mainChart = {
  interval: null,
  start: function(node) {
    mainChart.stop();

    let element = document.getElementById('current-usage');
    let time = new Date().getTime();
    let data = [[time, 20, 30]];

    let current_usage = new Dygraph(element, data, {
      // TODO fix up fake data, make start() pass node array
      drawPoints: true,
      animatedZooms: true,
      rollPeriod: 5,
      showRoller: true,
      title: (node['description'] + ', node 1'),
      // time - 1 minute
      axes: {
        x: {
          axisLabelWidth: 100,
          axisLabelFormatter: function(time) {
            return new Date(time).toLocaleTimeString();
          },
          valueFormatter: function (time) {
            return new Date(time).toLocaleTimeString();
          }
        }
      },
      labels: ['Time', node['node_id'].toString(), '1']
    });

    mainChart.interval = setInterval(function () {
      getDataRange([0, 1], new Date().getTime() - 10, new Date().getTime() + 10, (points) => {
        data = data.concat(points);
        current_usage.updateOptions({
          'file': data,
          'dateWindow': [new Date().getTime() - 10 * 5000, new Date().getTime()],
          'valueRange': [null, null]
        });
      });
    }, 1000);
  },

  stop: function() {
    if (mainChart.interval) {
      clearInterval(mainChart.interval);
    }
  }
}

let generateTopology = function () {
  getTopology((topology) => {
    getDevices((devices) => {
      for (let i in topology) {
        topology[i]['devices'] = [];
      }
      console.log(topology);

      let inactive_element = document.getElementById('inactive');
      while (inactive_element.hasChildNodes()) {
        inactive_element.removeChild(inactive_element.lastChild);
      }

      let inactive = []

      for (let i in devices) {
        device = devices[i];
        node_id = device['node_id'];

        if (node_id != -1) {
          topology[node_id.toString()]['devices'].push(device);
        } else {
          inactive.push(device);
        }
      }

      final_topology = topology;

      for (let i in inactive) {
        let element = document.createElement('div');
        element.classList.add('item');
        element.textContent = inactive[i]["description"];
        inactive_element.appendChild(element);
      }

      chartConfig = transformTopology(topology)

      let root = chartConfig['root'];

      if (Object.keys(root).length === 0 && root.constructor === Object) {
        return;
      }

      mainChart.start(root);

      new Treant(chartConfig);
    });
  });
}

let addBranch = function (id) {
  // TODO
  let xhr = new XMLHttpRequest();

  xhr.onload = function () {
    let response = JSON.parse(this.responseText);
    console.log(response);
  };

  xhr.open('post', 'branch/' + id + '/');
  xhr.send();
}
