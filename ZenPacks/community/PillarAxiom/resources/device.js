Ext.onReady(function() {

    var DEVICE_OVERVIEW_ID = 'deviceoverviewpanel_summary';
    Ext.ComponentMgr.onAvailable(DEVICE_OVERVIEW_ID, function(){
        var overview = Ext.getCmp(DEVICE_OVERVIEW_ID);

        overview.removeField('memory');        

        overview.addField({
            name: 'totalcapacity',
            fieldLabel: _t('Total Capacity') 
        });

        overview.addField({
            name: 'usedcapacity',
            fieldLabel: _t('Used Capacity')
        });

        overview.addField({
            name: 'freecapacity',
            fieldLabel: _t('Free Capacity')
        });
    });
});

Ext.onReady(function() {

    var DEVICE_OVERVIEW_ID = 'deviceoverviewpanel_descriptionsummary';
    Ext.ComponentMgr.onAvailable(DEVICE_OVERVIEW_ID, function(){
        var overview = Ext.getCmp(DEVICE_OVERVIEW_ID);
        overview.removeField('osManufacturer');
        overview.removeField('osModel');



    });
});

