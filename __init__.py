# -*- coding: utf-8 -*-
"""
/***************************************************************************
 mergeLayers
                                 A QGIS plugin
 Merge 2 layerd and attribute tables even if have different names.
                             -------------------
        begin                : 2016-02-09
        copyright            : (C) 2016 by Kay Warrie
        email                : kaywarrie@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load mergeLayers class from file mergeLayers.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mergeLayers import mergeLayers
    return mergeLayers(iface)
