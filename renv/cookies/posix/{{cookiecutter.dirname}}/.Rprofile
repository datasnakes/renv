# Author: Rob Gilmore
#
# This .Rprofile is used to get a more specific local library
# path (.libPaths()) for even minor versions of R.  The local library
# path is where bioconductor/cran/github packages are stored in each
# users home directory.
#
# Keeping the local libraries seperate for each minor version of R
# on the MCSR will keep pipelines from breaking because of dependency
# issues as well as others (see below).
#

# Set repositories for CRAN
local({
  r <- getOption("repos")
  r["CRAN"] <- "{{cookiecutter.__CRAN_MIRROR__}}"
  r["CRANextra"] <- "{{cookiecutter.__CRANEXTRA_MIRROR__}}"
  options(repos=r)
})

# Ask the user a yes or no question
askYesNo <- function(msg) {
    ansr <- readline(prompt=msg)
    ansr <- tolower(ansr)
    acceptable_ansr <- c("yes", "no", "n", "y")
    while(!any(grep(ansr, acceptable_ansr, fixed=TRUE)) | ansr == "") {
    	ansr <- readline(prompt=msg)
	ansr <- tolower(ansr)
    }

    if (any(grep(ansr, c("yes", "y")))) {
	ret_log = TRUE
    } else {
    	ret_log = FALSE
    }
    return(ret_log)
}

# List of default packages to install based on the users need
standard_pkg_list <- {{cookiecutter.__STANDARD_PKG_LIST__}}
reproducible_wf_pkg_list <- {{cookiecutter.__REPRODUCIBLE_WORKFLOW_PKG_LIST__}}

# Checker for the default packages; also displays helpful output
checker_for_packages <-function(pkgs=list()) {
  # Format package names for output
  pkg_checklist <- list()
  for (pkg in names(pkgs)) {
    fmt_pkg_name <- pkgs[[pkg]]
    load_msg <- sprintf("\n..................Attempting to Load %s...................\n", fmt_pkg_name)
    message(load_msg)
    pkg_is_available <- require(pkg, quietly = TRUE, character.only = TRUE)
    if (!pkg_is_available) {
      warn_msg <- sprintf("Prompting for %s Installation...\n", fmt_pkg_name)
      prompt_msg <- sprintf("Do you want to install %s??? [Y/N]\n", fmt_pkg_name)

      warning(warn_msg, immediate.=TRUE, call.=FALSE)
      answer <- askYesNo(prompt_msg)
    } else {
      answer = FALSE
      msg <- sprintf("\n.................%s is installed!..................\n", fmt_pkg_name)
      message(msg)
    }
    pkg_checklist[[pkg]] <- answer
  }
  return(pkg_checklist)
}

# Installer for default packages
installer_for_packages <- function(lib, pkgs=list()) {
  for (pkg in names(pkgs)) {
    fmt_pkg_name <- pkgs[[pkg]]
    message("")
    warn_msg <- sprintf("Installing %s from %s/.Rprofile.\n into %s", fmt_pkg_name, getwd(), lib)
    warning(warn_msg, immediate.=TRUE, call.=FALSE)
    if (pkg == "BiocInstaller") {
      warning("\nBioconductor will also install several other packages.\n")
      installer_for_bioconductor(lib = lib)
    } else if (pkg %in% names(reproducible_wf_pkg_list)) {
      message("%s is in the list of Reproducible Workflow Packages and requires an installation with devtools.")
      install.packages("devtools")
      if (pkg == "miniCRAN") {
        devtools::install_github("RevolutionAnalytics/miniCRAN")
      } else if (pkg == "packrat") {
        devtools::install_github("rstudio/packrat")
      }
    } else {
      install.packages(pkg)
      }
    install_msg <- sprintf("\n..............%s was successfully installed!!...............\n", fmt_pkg_name)
    message(install_msg)
  }
}

# Installer for biocLite/bioconductor
installer_for_bioconductor <- function(lib, download=FALSE) {
  # Option for Downloading the biocLite.R script manually
  if (download) {
    system2("rm", args=c("~/biocLite.R"))
    system2("wget", args=c("-O", "~/biocLite.R", "http://bioconductor.org/biocLite.R"), wait=TRUE)
  } else {
    # Install Bioconductor
    source("https://bioconductor.org/biocLite.R")
    message("\n..............Bioconductor was successfully installed...............\n")
    # Add BiocInstaller to the defaultPackages option
    options(defaultPackages=c(getOption("defaultPackages"), "BiocInstaller"))
    # Add Bioconductor to the repos option
    r <- getOption('repos')["CRAN"]
    r <- c(r, BiocInstaller::biocinstallRepos())
    options(repos = r)
  }
}

# Main script that loads on interactive session
local( {
# Only execute on interactive session in a local environment
# This prevents infinite looping
  if(interactive()) {
    # Quietly load utils, append the libPaths, and create the proper directories if they don't already exist
    require(utils, quietly=TRUE)
    .libPaths(Sys.getenv("R_LIBS_USER"))
    if (!dir.exists(Sys.getenv("R_LIBS_USER"))) {
      dir.create(Sys.getenv("R_LIBS_USER"), recursive=TRUE)
    }
    # Check to see if the any packages from the package lists are installed
    std_pkg_checklist <- checker_for_packages(standard_pkg_list)
    rep_workflow_checklist <- checker_for_packages(reproducible_wf_pkg_list)
    checklist <- c(std_pkg_checklist, rep_workflow_checklist)
    # Install packages that are required by the user
    pkgs <- c(standard_pkg_list, reproducible_wf_pkg_list)
    pkgs_to_install <- pkgs[!checklist == FALSE]
    installer_for_packages(lib=Sys.getenv("R_LIBS_USER"), pkgs = pkgs_to_install)

  	} # interactive
  }
) # local
