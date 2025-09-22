# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of TrustCAD Analyzer
- DXF file upload and processing functionality
- Automatic traffic equipment detection system
- Support for 16+ types of traffic control equipment
- Multi-user project management system
- Project editor with item management
- Report generation (HTML, Excel, DXF)
- User authentication and session management

### Features
- **DXF Shape Analysis**: Automatic detection of traffic equipment from CAD drawings
- **Project Management**: Create, edit, and manage multiple projects
- **Equipment Detection**: Support for poles, vehicle signals, pedestrian signals, controllers, and more
- **Report Generation**: Generate construction reports in multiple formats
- **Color-coded Output**: Excel files with color-coded DXF entities
- **DXF Regeneration**: Export modified DXF files with updated colors

### Supported Equipment Types

#### 01-Group: Poles
- Dedicated pole (01-01)
- Kanden pole (01-02) 
- Lighting pole (01-04, 01-05, 01-06)

#### 02-Group: Vehicle Signals
- Horizontal 3-aspect (02-01)
- Double-face horizontal 3-aspect (02-02)
- Light box only horizontal 3-aspect (02-10)
- Vertical 3-aspect (02-13)
- Advance signal (02-14)
- Arrow signal (straight) (02-18)

#### 03-Group: Pedestrian Signals
- 2-aspect (embracing type) (03-01)

#### 04-Group: Equipment
- Controller (04-01)
- Accessory device (04-02)

#### 05-Group: Sensors
- Sensor arm (05-02)

#### 06-Group: Infrastructure
- Handhole (06-01)

### Technical Specifications
- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Jinja2 templates
- **File Processing**: ezdxf, pandas, openpyxl
- **Database**: SQLite
- **Authentication**: Flask-Login with password hashing

### System Requirements
- Python 3.8+
- Modern web browser (Chrome 80+, Firefox 75+, Edge 80+, Safari 13+)
- 4GB RAM recommended
- 1GB storage space

## [2.0.0] - 2025-09-22

### Added
- Advanced shape recognition system with geometric pattern matching
- Dynamic shape definition loading from external module
- Comprehensive project editor with drag-and-drop functionality
- Multi-format export capabilities
- User management with secure authentication

### Changed
- Complete rewrite of shape detection algorithms
- Improved user interface with Bootstrap 5
- Enhanced database schema for better project management
- Modular architecture for easier maintenance and extension

### Fixed
- Improved accuracy of automatic equipment detection
- Better handling of complex DXF files
- Enhanced error handling and user feedback

### Security
- Secure password hashing with werkzeug
- Session management with Flask-Login
- File upload validation and sanitization

## [1.0.0] - Initial Version

### Added
- Basic DXF to Excel conversion
- Simple shape counting functionality
- Basic web interface
- File upload capabilities

---

## Release Notes

### Version 2.0.0
This major release represents a complete overhaul of the TrustCAD Analyzer system. The new version features:

- **Enhanced Detection Accuracy**: Completely rewritten detection algorithms with geometric pattern matching
- **Professional UI**: Modern Bootstrap 5 interface with improved user experience  
- **Multi-user Support**: Full user authentication and project management system
- **Flexible Architecture**: Modular design allowing easy addition of new equipment types
- **Comprehensive Output**: Multiple export formats including HTML reports, Excel files, and DXF regeneration

### Migration from v1.0
Users upgrading from version 1.0 will need to:
1. Create new user accounts
2. Re-upload DXF files to new project system
3. Review detection results as algorithms have been significantly improved

### Known Issues
- Large DXF files (>10MB) may experience slower processing times
- Complex nested block structures in DXF files may not be fully supported
- Browser compatibility may vary with older versions

### Future Roadmap
- Support for additional CAD formats (DWG, etc.)
- Advanced reporting templates
- Batch processing capabilities
- API endpoints for integration
- Mobile-responsive interface improvements