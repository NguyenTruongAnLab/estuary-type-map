# Contributing to Global Estuary Type Map

Thank you for your interest in contributing to this project! We welcome contributions from the scientific community, developers, and anyone passionate about coastal ecosystems.

## 📋 AI Agent and Copilot Instructions

**For GitHub Copilot users and AI agents**: Please review the comprehensive project guidelines in [`.github/copilot-instructions.md`](.github/copilot-instructions.md) before making contributions. This document provides:
- Detailed project mandate and scientific principles
- Data sources and provenance requirements
- Code standards and best practices
- Common tasks and workflows
- Testing and validation procedures
- Emergency troubleshooting procedures

The instructions ensure all contributions maintain scientific integrity, data transparency, and code quality standards.

---

## Ways to Contribute

### 1. Add New Estuaries

To add new estuaries to the dataset:

1. Ensure the estuary is documented in peer-reviewed scientific literature
2. Edit `scripts/process_estuary_data.py`
3. Add a new feature to the `estuaries` FeatureCollection with:
   - Accurate coordinates (longitude, latitude)
   - Proper geomorphological classification
   - Country/region information
   - Description with scientific basis
   - Area (km²) if available
   - Depth (m) if available
   - Associated river(s) if applicable

Example:
```python
{
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
    "properties": {
        "name": "Your Estuary Name",
        "type": "Delta",  # or Fjord, Lagoon, Ria, Coastal Plain, Bar-Built, Tectonic
        "country": "Country Name",
        "description": "Scientific description based on literature",
        "area_km2": 1000,
        "depth_m": 50,
        "river": "River Name"
    }
}
```

4. Run the data processing script: `python3 scripts/process_estuary_data.py`
5. Test the changes locally
6. Submit a pull request with:
   - Reference to scientific source
   - Justification for classification
   - Any relevant notes

### 2. Improve Scientific Content

Help improve the accuracy and completeness of:
- Estuary type definitions
- Scientific references
- Classification criteria
- Documentation

### 3. Enhance Features

Technical improvements welcome:
- Better filtering options
- Search functionality
- Statistics and charts
- Performance optimizations
- Accessibility improvements
- Mobile experience enhancements

### 4. Fix Bugs

Found a bug? Please:
1. Check if it's already reported in Issues
2. If not, create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Browser/environment details
3. If you can fix it, submit a PR!

### 5. Documentation

Help improve:
- README clarity
- Technical documentation
- Usage examples
- API documentation
- Comments in code

## Contribution Guidelines

### Code Standards

- **JavaScript**: Use ES6+ features, consistent indentation (4 spaces)
- **Python**: Follow PEP 8 style guide
- **CSS**: Organize by component, use meaningful class names
- **HTML**: Semantic HTML5, proper indentation

### Commit Messages

Use clear, descriptive commit messages:
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep first line under 72 characters
- Add details in subsequent lines if needed

Examples:
```
Add Chesapeake Bay tributary estuaries

Update scientific definition for bar-built estuaries
Based on Smith et al. (2023) revised classification

Fix filter checkbox behavior on mobile devices
```

### Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Make** your changes
4. **Test** thoroughly
5. **Commit** with clear messages
6. **Push** to your fork
7. **Submit** a pull request

#### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Changes are tested and working
- [ ] Documentation is updated if needed
- [ ] Scientific sources are cited for new data
- [ ] No console errors or warnings
- [ ] Existing functionality is not broken
- [ ] Commit messages are clear and descriptive

### Scientific Accuracy

This project prioritizes scientific accuracy:

- **Always cite sources** for new estuary data
- **Use peer-reviewed literature** when possible
- **Verify classifications** match accepted scientific criteria
- **Check coordinates** for accuracy
- **Document uncertainties** when classification is ambiguous

### Testing Your Changes

Before submitting:

1. Run the Python script: `python3 scripts/process_estuary_data.py`
2. Start a local server: `python3 -m http.server 8000`
3. Open `http://localhost:8000` in your browser
4. Test all features:
   - Map loads correctly
   - Markers display at right locations
   - Popups show correct information
   - Filters work properly
   - No JavaScript errors in console
5. Test on different browsers if possible
6. Test responsive design on mobile

## Questions?

- **Issues**: For bugs, feature requests, or questions
- **Discussions**: For general questions or ideas
- **Email**: Contact repository maintainer for sensitive matters

## Code of Conduct

Be respectful and constructive:
- Welcome newcomers
- Provide helpful feedback
- Respect different perspectives
- Focus on scientific accuracy
- Maintain professional communication

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- CONTRIBUTORS.md file
- Project documentation

Significant contributions may be acknowledged in scientific publications using this tool.

## License

By contributing, you agree that your contributions will be licensed under the same terms as the project (see LICENSE file).

## Thank You!

Your contributions help make this tool more valuable for researchers, educators, and anyone interested in understanding Earth's coastal systems. Every improvement, no matter how small, is appreciated!
