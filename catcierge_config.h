//
// This file is part of the Catcierge project.
//
// Copyright (c) Joakim Soderberg 2013-2015
//
//    Catcierge is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 2 of the License, or
//    (at your option) any later version.
//
//    Foobar is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with Catcierge.  If not, see <http://www.gnu.org/licenses/>.
//

#ifndef __CATCIERGE_CONFIG_H__
#define __CATCIERGE_CONFIG_H__

#define CATCIERGE_VERSION_STR "unknown"

#define CATCIERGE_HAVE_UNISTD_H 1
#define CATCIERGE_HAVE_FCNTL_H 1
#define CATCIERGE_HAVE_SYS_TYPES_H 1
#define CATCIERGE_HAVE_SYS_STAT_H 1
/* #undef CATCIERGE_HAVE_PWD_H */
/* #undef CATCIERGE_HAVE_GRP_H */
/* #undef CATCIERGE_HAVE_PTY_H */
/* #undef CATCIERGE_HAVE_UTIL_H */

#define CATCIERGE_GIT_HASH ""
#define CATCIERGE_GIT_HASH_SHORT ""
#define CATCIERGE_GIT_TAINTED 

#if (CATCIERGE_HAVE_SYS_TYPES_H && CATCIERGE_HAVE_PWD_H && CATCIERGE_HAVE_GRP_H)
#define CATCIERGE_ENABLE_DROP_ROOT_PRIVILEGES
#endif

/* #undef CATCIERGE_GUI_TESTS */

#define CATCIERGE_CONF_PATH "/etc/catcierge/catcierge.cfg"
#define CATCIERGE_LOCKOUT_GPIO 4
#define CATCIERGE_BACKLIGHT_GPIO 18

#ifdef RPI
#define CATCIERGE_RPI_CONF_PATH "/etc/catcierge/catcierge-rpi.cfg"
#endif

#endif // __CATCIERGE_CONFIG_H__

