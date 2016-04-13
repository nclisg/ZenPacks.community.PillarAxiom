from Products.DataCollector.plugins.CollectorPlugin import (SnmpPlugin, GetTableMap, GetMap)
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap, MultiArgs

__doc__ = """PillarAxiomMap
Gathers component information from Pillar Axiom storage systems
"""

class PillarAxiomMap(SnmpPlugin):

    snmpGetTableMaps = (
        GetTableMap(
            'sPilotInformationControlUnitTable', '.1.3.6.1.4.1.15548.2.2.3.2.1', {
                '.2': 'sPilotInformationControlUnitPilotIdentity',
                '.3': 'sPilotInformationControlUnitOperationMode',
                '.9': 'sPilotInformationControlUnitSerialNumber',
                '.10': 'sPilotInformationControlUnitOSVersion',
                '.11': 'sPilotInformationControlUnitPacmanVersion',
                '.12': 'sPilotInformationControlUnitHardwareComponentStatus',
                }
            ),

        GetTableMap(
            'sBrickInformationTable', '.1.3.6.1.4.1.15548.2.2.2.1.1', {
                '.5':'sBrickInformationName',
                '.6':'sBrickInformationSerialNumber',
                '.7':'sBrickInformationOverallBrickStatus',
                '.8':'sBrickInformationBrickFruStatusRollup',
                '.9':'sBrickInformationTemperateStatusRollup',
                }
            ),

        GetTableMap(
            'sBrickInformationNodeDiskDriveTable', '.1.3.6.1.4.1.15548.2.2.2.3.1', {
                '.2':'sBrickInformationBrickNodeDiskDriveStatus',
                '.3':'sBrickInformationBrickNodeDiskDriveModel',
                '.4':'sBrickInformationBrickNodeDiskDriveSerialNumber',
                '.5':'sBrickInformationBrickNodeDiskDriveFirmwareVersion',
                '.6':'sBrickInformationBrickNodeDiskDriveDriveSlot',
                '.7':'sBrickInformationBrickNodeDiskDriveSpare',
                '.8':'sBrickInformationBrickNodeDiskDriveCapacity',
                }
            ),

        GetTableMap(
            'cLunInformationTable', '.1.3.6.1.4.1.15548.2.1.2.2.2.1.1.1', {
                '.5': 'cLunInformationPhysicalAllocatedCapacity',
                '.15': 'cLunInformationLuid',
                '.16': 'cLunInformationName',
                '.20': 'cLunInformationVolumeGroupIdentityFqn',
                '.24': 'cLunInformationStorageDomainIdentityFqn',
                '.28': 'cLunInformationProfileIdentityFqn',
                '.29': 'cLunInformationQosInformationRedundancy',
                '.30': 'cLunInformationQosInformationPerformanceBand',
                '.37': 'cLunInformationStatus',
                }
            ),

        GetTableMap(
            'cVolumeGroupTable', '.1.3.6.1.4.1.15548.2.1.2.4.1.1', {
                '.4': 'cVolumeGroupDetailsVolumeGroupName',
                '.8': 'cVolumeGroupDetailsAllocatedCapacity',
                '.9': 'cVolumeGroupDetailsUsedCapacity',
                '.10': 'cVolumeGroupDetailsPhysicalAllocatedCapacity',
                '.11': 'cVolumeGroupDetailsPhysicalUsedCapacity',
                }
            ),

        GetTableMap(
            'pSanFcPortStatisticsV2Table', '.1.3.6.1.4.1.15548.2.3.9.1.1', {
                '.3': 'pSanFcPortStatisticsV2SlammerFQN',
                '.4': 'pSanFcPortStatisticsV2ControlUnitNumber',
                '.5': 'pSanFcPortStatisticsV2PortName',
                }
            ),

        GetTableMap(
            'sSlammerInformationControlUnitNIMFibreChannelPortTable', '.1.3.6.1.4.1.15548.2.2.1.12.1', {
                '.5': 'sSlammerInformationControlUnitNIMFibreChannelPortStatus',
                '.6': 'sSlammerInformationControlUnitNIMFibreChannelPortSpeed',
                '.7': 'sSlammerInformationControlUnitNIMFibreChannelPortWWN',
                }
            ),
        )

    snmpGetMap = GetMap(
         {
            '.1.3.6.1.4.1.15548.2.1.1.4.1.1.14.1': 'setHWSerialNumber',
            '.1.3.6.1.4.1.15548.2.1.2.3.1.1.2.1': 'totalcapacity',
            '.1.3.6.1.4.1.15548.2.1.2.3.1.1.3.1': 'usedcapacity',
            '.1.3.6.1.4.1.15548.2.1.2.3.1.1.4.1': 'freecapacity',
	}
    )


    def capformat(self, value):
        return "{:,}".format(int(value)) + " GB"

    def process(self, device, results, log):
        log.info('processing %s for device %s', self.name(), device.id)

        maps = []
        pilotmap = []
        brickmap = []
        volumegroupmap = []
        fcportmap = []

	bricknames = []
        volumegroupnames = []

        getdata, tabledata = results

        pilottable = tabledata.get('sPilotInformationControlUnitTable', {})
        bricktable = tabledata.get('sBrickInformationTable', {})
        disktable = tabledata.get('sBrickInformationNodeDiskDriveTable', {})
        luntable = tabledata.get('cLunInformationTable', {})
        volumegrouptable = tabledata.get('cVolumeGroupTable', {})
        pfcporttable = tabledata.get('pSanFcPortStatisticsV2Table', {})
        sfcporttable = tabledata.get('sSlammerInformationControlUnitNIMFibreChannelPortTable', {})

        # Axiom Device

        total = getdata.get('totalcapacity')
        used = getdata.get('usedcapacity')
        free = getdata.get('freecapacity')
        usedpercent = int(float(used) / float(total) * 100)

        maps.append(ObjectMap(
            modname = 'ZenPacks.community.PillarAxiom.PillarAxiomDevice',
            data = {
                'setHWSerialNumber': getdata.get('setHWSerialNumber'),
                'totalcapacity': self.capformat(total),
                'usedcapacity': self.capformat(used) + ' (' + str(usedpercent) + '%)',
                'freecapacity': self.capformat(free) + ' (' + str(100 - usedpercent) + '%)',
            }))

	# Pilot Component
        for snmpindex, row in pilottable.items():
            name = row.get('sPilotInformationControlUnitPilotIdentity')

            if not name:
                log.warn('Skipping pilot with no name')
                continue

            pilotmap.append(ObjectMap({
                'id': self.prepId(name),
                'title': name,
                'snmpindex': snmpindex.strip('.'),
                'pilotmode': row.get('sPilotInformationControlUnitOperationMode'),
                'pilotserial': row.get('sPilotInformationControlUnitSerialNumber'),
                'pilotosversion': row.get('sPilotInformationControlUnitOSVersion'),
                'pilotserverversion': row.get('sPilotInformationControlUnitPacmanVersion'),
                'pilotstatus': row.get('sPilotInformationControlUnitHardwareComponentStatus'),
                }))


        maps.append(RelationshipMap(
            relname = 'axiomPilots',
            modname = 'ZenPacks.community.PillarAxiom.AxiomPilot',
            objmaps = pilotmap))

       # Brick Component

        for snmpindex, row in bricktable.items():
            name = row.get('sBrickInformationName')
            if not name:
                log.warn('Skipping brick with no name')
                continue
            bricknames.append(name)
            brickmap.append(ObjectMap({
                'id': self.prepId(name),
                'title': name,
                'snmpindex': snmpindex.strip('.'),
                'brickserial': row.get('sBrickInformationSerialNumber'),
                'brickstatus': row.get('sBrickInformationOverallBrickStatus'),
                'brickfrustatus': row.get('sBrickInformationBrickFruStatusRollup'),
                'bricktempstatus': row.get('sBrickInformationTemperateStatusRollup'),
                }))

        maps.append(RelationshipMap(
            relname = 'axiomBricks',
            modname = 'ZenPacks.community.PillarAxiom.AxiomBrick',
            objmaps = brickmap))

        # Disk Component

        for brick in bricknames:
            diskmap = []
            for snmpindex, row in disktable.items():
                # do check for no data?
                name = snmpindex.strip('.')
                diskbrick = bricknames[int(name.split('.')[0])-1]

                if brick == diskbrick:
                    diskmap.append(ObjectMap({
                    'id': self.prepId(name),
                    'title': name,
                    'snmpindex': snmpindex.strip('.'),
                    'diskstatus': row.get('sBrickInformationBrickNodeDiskDriveStatus'),
                    'diskmodel': row.get('sBrickInformationBrickNodeDiskDriveModel'),
                    'diskserial': row.get('sBrickInformationBrickNodeDiskDriveSerialNumber'),
                    'diskfirmware': row.get('sBrickInformationBrickNodeDiskDriveFirmwareVersion'),
                    'diskslot': row.get('sBrickInformationBrickNodeDiskDriveDriveSlot'),
                    'diskspare': row.get('sBrickInformationBrickNodeDiskDriveSpare'),
                    'diskcapacity': row.get('sBrickInformationBrickNodeDiskDriveCapacity'),
                    }))

            maps.append(RelationshipMap(
                compname= 'axiomBricks/%s' % brick,
                relname = 'axiomDisks',
                modname = 'ZenPacks.community.PillarAxiom.AxiomDisk',
                objmaps = diskmap))

        # Volume Group Component

        for snmpindex, row in volumegrouptable.items():
            name = row.get('cVolumeGroupDetailsVolumeGroupName')
            if not name:
                name = "root"

            volumegroupnames.append(name)
            volumegroupmap.append(ObjectMap({
                'id': self.prepId(name),
                'title': name,
                'snmpindex': snmpindex.strip('.'),
                'vgallocatedcapacity': "{:,}".format(row.get('cVolumeGroupDetailsAllocatedCapacity')),
                'vgusedcapacity': "{:,}".format(row.get('cVolumeGroupDetailsUsedCapacity')),
                'vgphysicalallocatedcapacity': "{:,}".format(row.get('cVolumeGroupDetailsPhysicalAllocatedCapacity')),
                'vgphysicalusedcapacity': "{:,}".format(row.get('cVolumeGroupDetailsPhysicalUsedCapacity')),
                }))

        volumegroupnames.append('None')

        maps.append(RelationshipMap(
            relname = 'axiomVolumeGroups',
            modname = 'ZenPacks.community.PillarAxiom.AxiomVolumeGroup',
            objmaps = volumegroupmap))


        # LUN Component

        for volumegroup in volumegroupnames:
            lunmap = []
            for snmpindex, row in luntable.items():
                name = row.get('cLunInformationName')
                if not name:
                    log.warn('Skipping lun with no name')
                    continue

                lunvolumegroup = row.get('cLunInformationVolumeGroupIdentityFqn')[1:]
                if not lunvolumegroup:
                    lunvolumegroup = 'root'

                if volumegroup == lunvolumegroup:
                    lunmap.append(ObjectMap({
                        'id': self.prepId(name),
                        'title': name,
                        'snmpindex': snmpindex.strip('.'),
                        'lunsize': "{:,}".format(row.get('cLunInformationPhysicalAllocatedCapacity')),
                        'lunid': row.get('cLunInformationLuid'),
                        'lundomain': row.get('cLunInformationStorageDomainIdentityFqn')[1:],
                        'lunprofile': row.get('cLunInformationProfileIdentityFqn')[1:],
                        'lunredundancy': row.get('cLunInformationQosInformationRedundancy'),
                        'lunpriority': row.get('cLunInformationQosInformationPerformanceBand'),
                        'lunstatus': row.get('cLunInformationStatus'),
                    }))

            maps.append(RelationshipMap(
                compname = 'axiomVolumeGroups/%s' % volumegroup,
                relname = 'axiomLuns',
                modname = 'ZenPacks.community.PillarAxiom.AxiomLun',
                objmaps = lunmap))

        # FC Port Component

        for snmpindex, row in pfcporttable.items():
            name = row.get('pSanFcPortStatisticsV2PortName')
            if not name:
                log.warn('Skipping FC Port with no name')
                continue
            query = '1.' + str(int(row.get('pSanFcPortStatisticsV2ControlUnitNumber')) + 1) + '.' +  str(int(name[4:]) + 1)
            sfcrow = sfcporttable.get(query)
            fcportmap.append(ObjectMap({
                'id': self.prepId(name),
                'title': name,
                'snmpindex': snmpindex.strip('.'),
                'fcportslammer': row.get('pSanFcPortStatisticsV2SlammerFQN')[1:],
                'fcportcontrolunitnumber': row.get('pSanFcPortStatisticsV2ControlUnitNumber'),
                'fcportstatus': sfcrow.get('sSlammerInformationControlUnitNIMFibreChannelPortStatus'),
                'fcportspeed': int(sfcrow.get('sSlammerInformationControlUnitNIMFibreChannelPortSpeed')) / 1000000000,
                'fcportwwn': sfcrow.get('sSlammerInformationControlUnitNIMFibreChannelPortWWN'),
                }))

        maps.append(RelationshipMap(
            relname = 'axiomFCPorts',
            modname = 'ZenPacks.community.PillarAxiom.AxiomFCPort',
            objmaps = fcportmap))


        return maps

