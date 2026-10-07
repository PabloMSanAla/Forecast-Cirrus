#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <algorithm>
#include <yaml-cpp/yaml.h>

namespace forecast {

struct Config {
    // 1. Simulation
    std::string sim_name = "TNG";
    double box_size_mpc_over_h = 35.0;
    std::string snapshots_dir = "";
    std::string snaplist_file = "";
    std::string timelist_file = "";
    std::string redshift_list_file = "";
    std::string comoving_distances_file = "";

    // 2. Geometry
    double source_redshift = 0.69;
    double fov_degrees = 1.16;
    double resolution_arcsec = 0.1;
    std::string planes_list_file = "";
    long seed_center = 121;
    long seed_face = 1210;
    long seed_sign = 2101;

    // 3. Stellar Population Synthesis (SPS)
    std::string sps_model = "bc03";
    std::string sps_imf = "chabrier";
    std::string bc03_dir = "";
    std::string filters_file = "";
    std::string filters_dir = "";

    // 4. Extinction & Gas (DC module)
    int dc_read_gas_mode = 1;
    double dc_mag_limit_filter_0 = 33.5;
    std::string dc_extinction_file = "";

    // 5. Execution & RAM
    double memory_ceiling_gb = 4.0;
    int default_num_workers = 4;
    size_t igm_chunk_size = 0;

    // 6. Output Directories
    std::string lc_output_dir = "";
    std::string df_output_dir = "";
    std::string dc_output_dir = "";
    std::string igm_output_dir = "";
    std::string image_output_dir = "";
    std::string logs_dir = "logs/";

    // 7. Create Image Options
    std::string image_target_filter = "Roman_WFI_f158";
    std::string image_catalog_source = "df";
    std::string image_catalog_dir = "";

    // Helper: checks if a filename ends with .yaml or .yml
    static bool isYaml(const std::string& path) {
        if (path.length() >= 5) {
            std::string ext5 = path.substr(path.length() - 5);
            std::transform(ext5.begin(), ext5.end(), ext5.begin(), ::tolower);
            if (ext5 == ".yaml") return true;
        }
        if (path.length() >= 4) {
            std::string ext4 = path.substr(path.length() - 4);
            std::transform(ext4.begin(), ext4.end(), ext4.begin(), ::tolower);
            if (ext4 == ".yml") return true;
        }
        return false;
    }

    // Resolves a relative path against the directory where the YAML config resides,
    // or against FORECAST_DIR / current working directory
    static std::string resolvePath(const std::string& base_dir, const std::string& p) {
        if (p.empty()) return "";
        std::filesystem::path fp(p);
        if (fp.is_absolute()) return p;
        if (!base_dir.empty()) {
            std::filesystem::path combined = std::filesystem::path(base_dir) / fp;
            if (std::filesystem::exists(combined)) {
                return combined.lexically_normal().string();
            }
        }
        for (const char* env_var : {"FORECAST_DIR", "FORECAST_ROOT"}) {
            const char* val = std::getenv(env_var);
            if (val && *val) {
                std::filesystem::path combined = std::filesystem::path(val) / fp;
                if (std::filesystem::exists(combined)) {
                    return combined.lexically_normal().string();
                }
            }
        }
        if (std::filesystem::exists(fp)) {
            return std::filesystem::absolute(fp).lexically_normal().string();
        }
        return p;
    }

    static Config load(const std::string& yaml_path) {
        Config cfg;
        YAML::Node root = YAML::LoadFile(yaml_path);
        std::filesystem::path ypath(yaml_path);
        std::string base_dir = ypath.has_parent_path() ? ypath.parent_path().string() : ".";

        // Simulation
        if (root["simulation"]) {
            auto sim = root["simulation"];
            if (sim["name"]) cfg.sim_name = sim["name"].as<std::string>();
            if (sim["box_size_mpc_over_h"]) cfg.box_size_mpc_over_h = sim["box_size_mpc_over_h"].as<double>();
            if (sim["snapshots_dir"]) cfg.snapshots_dir = resolvePath(base_dir, sim["snapshots_dir"].as<std::string>());
            if (sim["snaplist_file"]) cfg.snaplist_file = resolvePath(base_dir, sim["snaplist_file"].as<std::string>());
            if (sim["timelist_file"]) cfg.timelist_file = resolvePath(base_dir, sim["timelist_file"].as<std::string>());
            if (sim["redshift_list_file"]) cfg.redshift_list_file = resolvePath(base_dir, sim["redshift_list_file"].as<std::string>());
            if (sim["comoving_distances_file"]) cfg.comoving_distances_file = resolvePath(base_dir, sim["comoving_distances_file"].as<std::string>());
        }

        // Geometry
        if (root["geometry"]) {
            auto geom = root["geometry"];
            if (geom["source_redshift"]) cfg.source_redshift = geom["source_redshift"].as<double>();
            if (geom["fov_degrees"]) cfg.fov_degrees = geom["fov_degrees"].as<double>();
            if (geom["resolution_arcsec"]) cfg.resolution_arcsec = geom["resolution_arcsec"].as<double>();
            if (geom["planes_list_file"]) cfg.planes_list_file = resolvePath(base_dir, geom["planes_list_file"].as<std::string>());
            if (geom["randomization_seeds"]) {
                auto seeds = geom["randomization_seeds"];
                if (seeds["seed_1_center"]) {
                    std::string s = seeds["seed_1_center"].as<std::string>();
                    cfg.seed_center = std::stol(s, nullptr, 10);
                }
                if (seeds["seed_2_face"]) {
                    std::string s = seeds["seed_2_face"].as<std::string>();
                    cfg.seed_face = std::stol(s, nullptr, 10);
                }
                if (seeds["seed_3_sign"]) {
                    std::string s = seeds["seed_3_sign"].as<std::string>();
                    cfg.seed_sign = std::stol(s, nullptr, 10);
                }
            }
        }

        // SPS
        if (root["sps"]) {
            auto sps = root["sps"];
            if (sps["model"]) cfg.sps_model = sps["model"].as<std::string>();
            if (sps["imf"]) cfg.sps_imf = sps["imf"].as<std::string>();
            if (sps["bc03_dir"]) cfg.bc03_dir = resolvePath(base_dir, sps["bc03_dir"].as<std::string>());
            if (sps["filters_file"]) cfg.filters_file = resolvePath(base_dir, sps["filters_file"].as<std::string>());
            if (sps["filters_dir"]) cfg.filters_dir = resolvePath(base_dir, sps["filters_dir"].as<std::string>());
        }

        // Module-specific options
        if (root["modules"]) {
            auto mods = root["modules"];
            if (mods["dc"]) {
                auto dc = mods["dc"];
                if (dc["read_gas_mode"]) cfg.dc_read_gas_mode = dc["read_gas_mode"].as<int>();
                if (dc["mag_limit_filter_0"]) cfg.dc_mag_limit_filter_0 = dc["mag_limit_filter_0"].as<double>();
                if (dc["extinction_file"]) cfg.dc_extinction_file = resolvePath(base_dir, dc["extinction_file"].as<std::string>());
            }
            if (mods["igm"]) {
                auto igm = mods["igm"];
                if (igm["chunk_size_override"]) cfg.igm_chunk_size = igm["chunk_size_override"].as<size_t>();
            }
            if (mods["create_image"]) {
                auto img = mods["create_image"];
                if (img["target_filter"]) cfg.image_target_filter = img["target_filter"].as<std::string>();
                if (img["input_catalog_source"]) cfg.image_catalog_source = img["input_catalog_source"].as<std::string>();
                if (img["catalog_dir"]) cfg.image_catalog_dir = resolvePath(base_dir, img["catalog_dir"].as<std::string>());
            }
        }

        // Output paths
        if (root["paths"]) {
            auto paths = root["paths"];
            if (paths["lc_output_dir"]) cfg.lc_output_dir = resolvePath(base_dir, paths["lc_output_dir"].as<std::string>());
            if (paths["df_output_dir"]) cfg.df_output_dir = resolvePath(base_dir, paths["df_output_dir"].as<std::string>());
            if (paths["dc_output_dir"]) cfg.dc_output_dir = resolvePath(base_dir, paths["dc_output_dir"].as<std::string>());
            if (paths["igm_output_dir"]) cfg.igm_output_dir = resolvePath(base_dir, paths["igm_output_dir"].as<std::string>());
            if (paths["image_output_dir"]) cfg.image_output_dir = resolvePath(base_dir, paths["image_output_dir"].as<std::string>());
            if (paths["logs_dir"]) cfg.logs_dir = resolvePath(base_dir, paths["logs_dir"].as<std::string>());
        }

        // Execution
        if (root["execution"]) {
            auto exec = root["execution"];
            if (exec["memory_ceiling_gb"]) cfg.memory_ceiling_gb = exec["memory_ceiling_gb"].as<double>();
            if (exec["default_num_workers"]) cfg.default_num_workers = exec["default_num_workers"].as<int>();
        }

        // Ensure trailing slash on directory paths
        auto addSlash = [](std::string& s) {
            if (!s.empty() && s.back() != '/') s += '/';
        };
        addSlash(cfg.snapshots_dir);
        addSlash(cfg.bc03_dir);
        addSlash(cfg.filters_dir);
        addSlash(cfg.lc_output_dir);
        addSlash(cfg.df_output_dir);
        addSlash(cfg.dc_output_dir);
        addSlash(cfg.igm_output_dir);
        addSlash(cfg.image_output_dir);
        addSlash(cfg.image_catalog_dir);
        addSlash(cfg.logs_dir);

        // If image_catalog_dir not set, default to corresponding module output dir
        if (cfg.image_catalog_dir.empty()) {
            if (cfg.image_catalog_source == "df") cfg.image_catalog_dir = cfg.df_output_dir;
            else if (cfg.image_catalog_source == "dc") cfg.image_catalog_dir = cfg.dc_output_dir;
            else if (cfg.image_catalog_source == "igm") cfg.image_catalog_dir = cfg.igm_output_dir;
        }

        return cfg;
    }
};

} // namespace forecast
