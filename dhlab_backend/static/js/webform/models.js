// Generated by CoffeeScript 1.6.1
var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['vendor/backbone-min'], function(Backbone) {
  var xFormModel;
  xFormModel = (function(_super) {

    __extends(xFormModel, _super);

    function xFormModel() {
      return xFormModel.__super__.constructor.apply(this, arguments);
    }

    xFormModel.prototype.defaults = {
      id: null,
      children: []
    };

    return xFormModel;

  })(Backbone.Model);
  return xFormModel;
});