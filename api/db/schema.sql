DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS lesion;

CREATE TABLE `user` (
  `user_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `user_email` TEXT UNIQUE NOT NULL,
  `user_password` TEXT NOT NULL
);

CREATE TABLE `lesion` (
  `lesion_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `user_id` INTEGER NOT NULL,
  `lesion_img_url` TEXT NOT NULL,
  `lesion_malignancy` INT NOT NULL DEFAULT -1,
  `lesion_pred_conf` FLOAT NOT NULL DEFAULT -1,
  `lesion_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE `tokenblocklist` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `jti` VARCHAR(36) NOT NULL,
  `created_at` DATETIME NOT NULL
);

CREATE INDEX `jti_index` ON `tokenblocklist`(`jti`)