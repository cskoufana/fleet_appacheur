openerp.fleet_appacheur = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.DashBoard = instance.Widget.extend({
        template: "DashBoardTemplate",
        start: function() {
            console.log("pet store home page loaded");
            return new local.VehicleCost(this).appendTo(this.$('.oe_homepage_left'));
        },
    });

    instance.web.client_actions.add('fleet_appacheur.dashboard', 'instance.fleet_appacheur.DashBoard');

    local.VehicleCost = instance.Widget.extend({
        template : "VehicleCostBlock",
        events: {
            'click .oe_vehicle_id_link': 'selected_vehicle',
        },
    	start: function() {
            var self = this;
            var year = new Date().getFullYear()+"";
            var widget =  new instance.web.Model("fleet.vehicle")
                .call("get_costs_by_vehicles_and_costs_type",[],{context: new instance.web.CompoundContext({"fleet_order_by":"total","fleet_filter_year":year})})
                .then(function(result) {
                	console.log(result+" = "+result);
                    self.$el.append(QWeb.render("VehicleCost", {data:result}));
                	self.$el.find('.fleet-year-menu input[value="'+year+'"]').each(function () {
                		this.checked = "checked";
                	});
                	self.$el.find('.appacheur-fleet-table tbody .fleet-bar-animate').each(function(){
                		var delay = $(this).attr("width")+"0";
                		$(this).css("border-right-width","0px").animate({'border-right-width':$(this).attr("width")},700);
                	});
                	$('.fleet-amount').each(function () {
                	    var item = $(this).text();
                	    var num = Number(item).toLocaleString('fr');  
                	    $(this).text(num);
                	});
                	
                    self.$(".fleet_order_by").change(function() {
                    	if(this.checked){
                    		self.radio_clicked(self,this);
                    	}
                    });
                    self.$(".appacheur-fleet-menu input").change(function() {
                    	self.checkbox_clicked(self,this);
                    });
                    self.$( "#fleet_dialog" ).dialog({
                        autoOpen: false, 
                        height: 250,
                        width:500,
                        modal:true
                     });
                    self.$( "#print_button_before" ).click(function() {
                        $( "#fleet_dialog" ).dialog( "open" );
                        if($( "#print_button" ).attr("ok") != "ok"){
                        $( "#print_button" ).click(function() {
                        	$( ".appacheur-custom-title" ).text($( "#print_title" ).val());
                        	$( ".appacheur-custom-subtitle" ).text($( "#print_subtitle" ).val());
                            $( "#fleet_dialog" ).dialog( "close" );
                            window.print();
                         });
                        $( "#print_button" ).attr("ok","ok");
                    }
                     });
                });
            return widget;
        },
        selected_vehicle: function (event) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'fleet.vehicle',
                res_id: $(event.currentTarget).data('id'),
                views: [[false, 'form']],
            });
        },
        radio_clicked: function(parent,obj) {
        	var filter_year = "0";
        	parent.$el.find('.appacheur-fleet-menu.fleet-year-menu input').each(function(){
        		if(this.checked)
        			filter_year = filter_year +","+this.value;
        	});
        	var filter_month = "0";
        	parent.$el.find('.appacheur-fleet-menu.fleet-month-menu input').each(function(){
        		if(this.checked)
        			filter_month = filter_month +","+this.value;
        	});
        	var filter_type = "0";
        	parent.$el.find('.appacheur-fleet-menu.fleet-type-menu input').each(function(){
        		if(this.checked)
        			filter_type = filter_type +","+this.value;
        	});
        	
        	var widget =  new instance.web.Model("fleet.vehicle")
            .call("get_costs_by_vehicles_and_costs_type",[],{context: new instance.web.CompoundContext({"fleet_order_by":obj.value,"fleet_filter_year":filter_year,"fleet_filter_month":filter_month,"fleet_filter_type":filter_type})})
            .then(function(result) {
            	console.log(result+" = "+obj.value);
            	parent.$el.find('.appacheur-fleet-table tbody').remove();
            	var ht =  $.parseHTML(QWeb.render("VehicleCost", {data:result}));
            	parent.$el.find('#hiddendiv').html(ht);
            	parent.$el.find('.appacheur-fleet-table  thead').after(parent.$el.find('#hiddendiv').find('.appacheur-fleet-table tbody'));
            	parent.$el.find('#hiddendiv').html("");
            	obj.checked="checked";
            	$('.appacheur-fleet-table tbody .fleet-amount').each(function () {
            	    var item = $(this).text();
            	    var num = Number(item).toLocaleString('fr');  
            	    $(this).text(num);
            	});
            	parent.$el.find('.fleet-text').hide();
            	parent.$el.find('.fleet-text').fadeIn(500);
            	parent.$el.find('.appacheur-fleet-table tbody .fleet-bar').each(function(){
            		var delay = parseInt($(this).attr("width"))*20;
            		$(this).css("border-right-width","0px").animate({"border-right-width":$(this).attr("width")},delay);
            	});
            });
        },
        checkbox_clicked: function(parent,obj) {
        	var filter_year = 0;
        	var last_checked;
        	parent.$el.find('.appacheur-fleet-table .fleet_order_by').each(function(){
        		if(this.checked)
        			last_checked = this;
        	});
        	var filter_year = "0";
        	parent.$el.find('.appacheur-fleet-menu.fleet-year-menu input').each(function(){
        		if(this.checked)
        			filter_year = filter_year +","+this.value;
        	});
        	var filter_month = "0";
        	parent.$el.find('.appacheur-fleet-menu.fleet-month-menu input').each(function(){
        		if(this.checked)
        			filter_month = filter_month +","+this.value;
        	});
        	var filter_type = "0";
        	parent.$el.find('.appacheur-fleet-menu.fleet-type-menu input').each(function(){
        		if(this.checked)
        			filter_type = filter_type +","+this.value;
        	});
        	var widget =  new instance.web.Model("fleet.vehicle")
            .call("get_costs_by_vehicles_and_costs_type",[],{context: new instance.web.CompoundContext({"fleet_order_by":last_checked.value,"fleet_filter_year":filter_year,"fleet_filter_month":filter_month,"fleet_filter_type":filter_type})})
            .then(function(result) {
            	console.log(result+" = "+obj.value);
            	parent.$el.find('.all_block').remove();
            	var ht =  $.parseHTML(QWeb.render("VehicleCost", {data:result}));
            	parent.$el.find('#hiddendiv').html(ht);
            	parent.$el.find('.appacheur-fleet-menu.fleet-type-menu').after(parent.$el.find('#hiddendiv').find('.all_block'));
            	parent.$el.find('#hiddendiv').html("");
            	$('.fleet-amount').each(function () {
            	    var item = $(this).text();
            	    var num = Number(item).toLocaleString('fr');  
            	    $(this).text(num);
            	});
            	parent.$el.find('.fleet-text').hide();
            	parent.$el.find('.fleet-text').fadeIn(500);
            	parent.$el.find('.appacheur-fleet-table tbody .fleet-bar-animate').each(function(){
            		var delay = parseInt($(this).attr("width"))*20;
            		$(this).css("border-right-width","0px").animate({"border-right-width":$(this).attr("width")},delay);
            	});

                parent.$(".fleet_order_by").change(function() {
                	if(this.checked){
                		parent.radio_clicked(parent,this);
                	}
                });
            	parent.$el.find('.appacheur-fleet-table .fleet_order_by[value="'+last_checked.value+'"]').each(function () {
            		this.checked = "checked";
            	});
            });
        }
    });
}
