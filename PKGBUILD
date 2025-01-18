pkgname=python-clipsync
_pkgname=clipsync
pkgver=1.0.0
pkgrel=1
pkgdesc="the daemon that lives in your computer that shuttles wayland and xorg clipboards"
url=https://github.com/alexankitty/clipsync
arch=('any')
license=('GPLv2')
depends=('python' 'xclip' 'wl-clipboard')
optdepends=('cliphist: clipboard history support')
makedepends=('python-setuptools')
source=(git+https://github.com/alexankitty/${_pkgname}.git)
sha256sums=('SKIP')

build() {
    cd $_pkgname
    python -m build --wheel --no-isolation
}

package() {
    cd $_pkgname
    python -m installer --destdir="$pkgdir" dist/*.whl
}