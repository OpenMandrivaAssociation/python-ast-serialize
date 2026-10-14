%global _debugsource_template %{nil}
%define module ast_serialize

Name:		python-ast-serialize
Version:	0.13.0
Release:	1
Summary:	Python bindings for mypy AST serialization
# The extension is MIT. Vendored crates add Unicode-3.0, Unicode-DFS-2016,
# and one Apache-2.0 OR BSL-1.0 dependency. The rest allow MIT.
License:	MIT AND Unicode-3.0 AND Unicode-DFS-2016 AND (Apache-2.0 OR BSL-1.0)
Group:		Development/Python
URL:		https://github.com/mypyc/ast_serialize
Source0:	https://files.pythonhosted.org/packages/source/a/ast-serialize/ast_serialize-%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:	%{name}-%{version}-vendor.tar.xz
Source100:	%{name}.rpmlintrc
# Recreate the vendor archive after a version bump:
#   tar xf python-ast-serialize-VERSION.tar.gz
#   cd ast_serialize-VERSION
#   cargo vendor --locked vendor
#   tar cJf python-ast-serialize-VERSION-vendor.tar.xz vendor
#   abb store python-ast-serialize-VERSION-vendor.tar.xz

BuildSystem:	python
BuildRequires:	cargo
BuildRequires:	pkgconfig(python3)
BuildRequires:	python%{pyver}dist(maturin)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(wheel)

%description
ast_serialize is a Python extension that parses Python source and
serializes the AST in the binary format used by mypy.

%prep
%autosetup -n ast_serialize-%{version} -a1
# The crates are already vendored, so this build does not need rust-packaging.
mkdir -p .cargo
cat > .cargo/config.toml << 'EOF'
[net]
offline = true

[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

%build
export CARGO_NET_OFFLINE=true
export CARGO_HOME=$PWD/.cargo
%py_build
cargo tree --locked --offline --edges no-build,no-dev,no-proc-macro \
	--prefix none --format '{l}: {p}' \
	| sed -e "s: ($(pwd)[^)]*)::g" -e 's: / :/:g' -e 's:/: OR :g' \
	| sort -u > LICENSES.dependencies

%install
%py_install

%check
PYTHONPATH=%{buildroot}%{python_sitearch} %{__python} test_ast_serialize.py

%files
%doc README.md
# crates/LICENSE is the same MIT text and is already shipped inside dist-info.
%license LICENSE LICENSES.dependencies
%{python_sitearch}/%{module}
%{python_sitearch}/%{module}-%{version}.dist-info
