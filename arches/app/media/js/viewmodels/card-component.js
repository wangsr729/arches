define([
    'knockout',
    'underscore',
    'viewmodels/alert',
    'bindings/scrollTo'
], function(ko, _, AlertViewModel) {
    return function(params) {
        var self = this;
        var getTiles = function(tile, tiles) {
            tiles = tiles || [tile];
            tile.cards.forEach(function(card) {
                card.tiles().forEach(function(tile) {
                    tiles.push(tile);
                    getTiles(tile, tiles);
                });
            });
            return tiles;
        };
        this.configKeys = params.configKeys || [];
        this.showIds = params.showIds || false;
        this.state = params.state || 'form';
        this.preview = params.preview;
        this.loading = params.loading || ko.observable(false);
        this.card = params.card;
        this.card.showIds = this.showIds;
        this.tile = params.tile;
        this.reportExpanded = ko.observable(true);
        if (this.preview) {
            if (!this.card.newTile) {
                this.card.newTile = this.card.getNewTile();
            }
            this.tile = this.card.newTile;
        }
        this.form = params.form;
        this.provisionalTileViewModel = params.provisionalTileViewModel;
        this.reviewer = params.reviewer;
        this.expanded = ko.observable(true);
        this.beforeMove = function(e) {
            e.cancelDrop = (e.sourceParent!==e.targetParent);
        };
        this.startDrag = function(e, ui) {
            ko.utils.domData.get(ui.item[0], 'ko_sortItem').selected(true);
        };
        this.config = this.card.model ? this.card.model.get('config') : {};
        _.each(this.configKeys, function(key) {
            self[key] = self.config[key];
        });
        this.showChildCards = ko.computed(function() {
            return this.card.widgets().length === 0;
        }, this);
        this.getValuesByDatatype = function(type) {
            var values = {};
            if (self.tile && self.form) {
                var data = self.tile.getAttributes().data;
                _.each(data, function(value, key) {
                    var node = self.form.nodeLookup[key];
                    if (node && ko.unwrap(node.datatype) === type){
                        values[ko.unwrap(node.id)] = {
                            name: ko.unwrap(node.name),
                            value: value
                        };
                    }
                });
            }
            return values;
        };
        this.showHeaderLine = params.showHeaderLine;
        this.tiles = ko.computed(function() {
            var tiles = [];
            if (self.tile) {
                return getTiles(self.tile);
            } else {
                self.card.tiles().forEach(function(tile) {
                    getTiles(tile, tiles);
                });
            }
            return tiles;
        }, this);
        this.saveTile = function() {
            self.loading(true);
            self.tile.save(function(response) {
                self.loading(false);
                params.pageVm.alert(
                    new AlertViewModel(
                        'ep-alert-red',
                        response.responseJSON.title,
                        response.responseJSON.message,
                        null,
                        function(){}
                    )
                );
                if (params.form.onSaveError) {
                    params.form.onSaveError(self.tile);
                }
            }, function() {
                self.loading(false);
                if (params.form.onSaveSuccess) {
                    params.form.onSaveSuccess(self.tile);
                }
            });
        };
        this.deleteTile = function() {
            self.loading(true);
            self.tile.deleteTile(function(response) {
                self.loading(false);
                params.pageVm.alert(
                    new AlertViewModel(
                        'ep-alert-red',
                        response.responseJSON.title,
                        response.responseJSON.message,
                        null,
                        function(){}
                    )
                );
                if (params.form.onDeleteError) {
                    params.form.onDeleteError(self.tile);
                }
            }, function() {
                self.loading(false);
                if (params.form.onDeleteSuccess) {
                    params.form.onDeleteSuccess(self.tile);
                }
            });
        };
    };
});
