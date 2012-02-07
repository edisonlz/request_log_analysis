create database apilog;

CREATE TABLE `info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(50) NOT NULL,
  `value` int(11) NOT NULL,
  `date` varchar(50) NOT NULL,
  `type` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `info_type_index` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=3172 DEFAULT CHARSET=utf8;

CREATE TABLE `summery` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `total_reqs` int(11) NOT NULL,
  `uniq_ips` int(11) NOT NULL,
  `date` varchar(50) NOT NULL,
  `flow_rate` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `summery_date_index` (`date`)
) ENGINE=InnoDB AUTO_INCREMENT=112 DEFAULT CHARSET=utf8;



create index index_date on summery(date);

create index index_date on info(date);
create index index_type on info(type);
create index index_key on info(key);