%global cromite_commit fb75694894a4d87f4651d41f25377be6db03ce12
%global launcher_ver 8
%global chrome_lin64_sha256 2108e897a02827d87e2109784f4c5cfb5b5bfce3d2a99912022715805f5761d9
%global cromite_version_tag v%{version}-%{cromite_commit}
%define debug_package %{nil}

Name:           cromite
Version:        141.0.7390.70
Release:        1%{?dist}
Summary:        Cromite a Bromite fork with ad blocking and privacy enhancements (binary release)

License:        GPL3
URL:            https://github.com/uazo/cromite
# The commit hash in the URL should be updated along with the version
Source0:        https://github.com/uazo/cromite/releases/download/%{cromite_version_tag}/chrome-lin64.tar.gz
Source1:        https://github.com/foutrelis/chromium-launcher/archive/v%{launcher_ver}.tar.gz
Source2:        cromite.desktop
Source3:        cromite.svg
Source4:        LICENSE

# Minimal build dependencies: make for the launcher, binutils for strip.
BuildRequires:  make
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  gcc
BuildRequires:  glib2-devel

# Runtime dependencies from PKGBUILD
Requires:       alsa-lib
Requires:       gtk3
Requires:       libXScrnSaver
Requires:       nss
Requires:       fontconfig
Requires:       desktop-file-utils

# Optional dependencies from PKGBUILD, mapped to RPM package names
Recommends:     cups
Recommends:     pipewire-libs
Recommends:     libnotify
Recommends:     libsecret

# Suggested dependencies for desktop integration, not installed by default
Suggests:       kdialog
Suggests:       kwallet
Suggests:       libgnome-keyring
Suggests:       qt5-qtbase

%description
Cromite is a fork of Bromite, providing a privacy-focused browsing experience with
built-in ad blocking. This package contains the pre-compiled binary release.

%prep
# Create the main build directory and unpack Source0 into it.
# The -c option creates the directory before unpacking.
# The -n option sets the directory name.
# After this, rpmbuild cds into this directory.
%setup -q -c -n %{name}-%{version}

# Now we are in %{_builddir}/%{name}-%{version}
# Unpack the launcher archive (Source1) into the current directory.
# Source1 is chromium-launcher-8.tar.gz, which contains the chromium-launcher-8 directory.
tar xf %{SOURCE1}

%build
# The working directory is %{_builddir}/%{name}-%{version}.
# It contains chrome-lin/ (from Source0) and chromium-launcher-8/ (from Source1).
# Build the launcher
make CHROMIUM_NAME=cromite -C chromium-launcher-%{launcher_ver}

%install
# The working directory is %{_builddir}/%{name}-%{version}.
# Install launcher
make PREFIX=/usr DESTDIR=%{buildroot} CHROMIUM_NAME=cromite -C chromium-launcher-%{launcher_ver} install
install -Dm644 chromium-launcher-%{launcher_ver}/LICENSE %{buildroot}/usr/share/licenses/%{name}/LICENSE.launcher

# Create directories
install -d %{buildroot}/usr/lib/cromite
install -d %{buildroot}/usr/share/applications
install -d %{buildroot}/usr/share/icons/hicolor/scalable/apps
install -d %{buildroot}/usr/share/licenses/%{name}

# --- Install Cromite files ---
# The %setup macro already unpacked chrome-lin64.tar.gz which contains the 'chrome-lin' directory
cd %{_builddir}/%{name}-%{version}/chrome-lin

# Copy all contents to the destination directory.
cp -a ./* %{buildroot}/usr/lib/cromite/

# Now, work inside the final destination directory to make paths simpler and more robust.
cd %{buildroot}/usr/lib/cromite/

# The main executable is 'chrome', but the launcher executes /usr/lib/cromite/cromite.
mv chrome cromite

# Strip the main executables that we know for sure.
strip --strip-unneeded cromite chrome_sandbox chrome_crashpad_handler

# Strip all shared libraries (.so files) using a glob pattern. This is robust against future changes.
strip --strip-unneeded *.so

# The original chrome-wrapper is not needed because we use the chromium-launcher.
rm -f chrome-wrapper

# --- Install desktop and license files ---
cd %{_builddir}/%{name}-%{version}

install -Dm644 %{SOURCE2} %{buildroot}/usr/share/applications/cromite.desktop
install -Dm644 %{SOURCE3} %{buildroot}/usr/share/icons/hicolor/scalable/apps/cromite.svg
install -Dm644 %{SOURCE4} %{buildroot}/usr/share/licenses/%{name}/LICENSE

%files
/usr/bin/cromite
/usr/lib/cromite
/usr/share/applications/cromite.desktop
/usr/share/icons/hicolor/scalable/apps/cromite.svg
%license /usr/share/licenses/%{name}

%post
/usr/bin/update-desktop-database &> /dev/null || :

%postun
/usr/bin/update-desktop-database &> /dev/null || :

